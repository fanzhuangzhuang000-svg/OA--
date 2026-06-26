<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Mail;

/**
 * 告警通知服务
 *
 * 支持多渠道告警: 飞书 / 钉钉 / 企业微信 / 邮件
 * 用于系统监控指标超阈值时自动发送通知。
 *
 * 使用方式:
 *   AlertService::send('磁盘使用率超过 90%', 'critical', ['disk_percent' => 92]);
 *   AlertService::diskWarning(92);
 *   AlertService::dbConnectionHigh(150);
 */
class AlertService
{
    /** 告警级别 */
    public const LEVEL_INFO     = 'info';
    public const LEVEL_WARNING  = 'warning';
    public const LEVEL_CRITICAL = 'critical';

    /** 级别对应的 Emoji */
    private const LEVEL_EMOJI = [
        self::LEVEL_INFO     => 'ℹ️',
        self::LEVEL_WARNING  => '⚠️',
        self::LEVEL_CRITICAL => '🔴',
    ];

    /**
     * 发送告警到所有已启用的渠道
     */
    public static function send(string $message, string $level = self::LEVEL_WARNING, array $context = []): void
    {
        $emoji = self::LEVEL_EMOJI[$level] ?? '❓';
        $title = "[安防OA {$emoji}] " . ucfirst($level) . ' Alert';
        $timestamp = now()->toIso8601String();

        $fullMessage = implode("\n", [
            "{$title}",
            "━━━━━━━━━━━━━━━━━━",
            "📋 {$message}",
            "🕐 时间: {$timestamp}",
            "🏷️ 环境: " . app()->environment(),
        ]);

        if (!empty($context)) {
            $fullMessage .= "\n📊 详情:";
            foreach ($context as $key => $value) {
                $fullMessage .= "\n  • {$key}: {$value}";
            }
        }

        // 飞书
        if (config('monitoring.alert_channels.feishu.enabled')) {
            self::sendFeishu($fullMessage, $level);
        }

        // 钉钉
        if (config('monitoring.alert_channels.dingtalk.enabled')) {
            self::sendDingtalk($fullMessage, $level);
        }

        // 企业微信
        if (config('monitoring.alert_channels.wechat_work.enabled')) {
            self::sendWechatWork($fullMessage, $level);
        }

        // 邮件
        if (config('monitoring.alert_channels.mail.enabled')) {
            self::sendMail($title, $fullMessage);
        }

        // 本地日志（始终记录）
        Log::channel('daily')->warning("ALERT [{$level}] {$message}", $context);
    }

    // ========== 便捷方法 ==========

    public static function diskWarning(float $percent): void
    {
        self::send(
            "磁盘使用率达到 {$percent}%",
            $percent >= 95 ? self::LEVEL_CRITICAL : self::LEVEL_WARNING,
            ['disk_percent' => $percent, 'threshold' => config('monitoring.thresholds.disk_warn_percent')]
        );
    }

    public static function dbConnectionHigh(int $count): void
    {
        self::send(
            "数据库连接数过高: {$count}",
            $count >= config('monitoring.thresholds.db_connections_crit') ? self::LEVEL_CRITICAL : self::LEVEL_WARNING,
            ['connections' => $count]
        );
    }

    public static function slowQueryAlert(int $count): void
    {
        self::send(
            "检测到 {$count} 条慢查询",
            $count >= config('monitoring.thresholds.slow_queries_crit') ? self::LEVEL_CRITICAL : self::LEVEL_WARNING,
            ['slow_queries' => $count]
        );
    }

    public static function cacheHitRateLow(float $rate): void
    {
        self::send(
            "缓存命中率低于阈值: {$rate}%",
            $rate <= config('monitoring.thresholds.cache_hit_rate_crit') ? self::LEVEL_CRITICAL : self::LEVEL_WARNING,
            ['hit_rate' => $rate]
        );
    }

    public static function errorSpike(int $count24h): void
    {
        self::send(
            "24小时内错误数量异常: {$count24h} 条",
            $count24h >= config('monitoring.thresholds.errors_24h_crit') ? self::LEVEL_CRITICAL : self::LEVEL_WARNING,
            ['errors_24h' => $count24h]
        );
    }

    public static function backupStale(float $ageDays): void
    {
        self::send(
            "最近备份已过期 {$ageDays} 天",
            $ageDays >= config('monitoring.thresholds.backup_age_crit') ? self::LEVEL_CRITICAL : self::LEVEL_WARNING,
            ['backup_age_days' => $ageDays]
        );
    }

    public static function serviceDown(string $service, string $error = ''): void
    {
        self::send(
            "服务不可用: {$service}",
            self::LEVEL_CRITICAL,
            ['service' => $service, 'error' => $error]
        );
    }

    // ========== 渠道实现 ==========

    private static function sendFeishu(string $message, string $level): void
    {
        try {
            $webhook = config('monitoring.alert_channels.feishu.webhook');
            if (empty($webhook)) return;

            $color = match ($level) {
                self::LEVEL_CRITICAL => 'red',
                self::LEVEL_WARNING  => 'orange',
                default              => 'blue',
            };

            Http::timeout(5)->post($webhook, [
                'msg_type' => 'interactive',
                'card' => [
                    'header' => [
                        'title'    => ['content' => '安防OA 告警通知', 'tag' => 'plain_text'],
                        'template' => $color,
                    ],
                    'elements' => [
                        ['tag' => 'markdown', 'content' => $message],
                    ],
                ],
            ]);
        } catch (\Throwable $e) {
            Log::error('AlertService: feishu send failed', ['error' => $e->getMessage()]);
        }
    }

    private static function sendDingtalk(string $message, string $level): void
    {
        try {
            $webhook = config('monitoring.alert_channels.dingtalk.webhook');
            if (empty($webhook)) return;

            // 加签
            $secret = config('monitoring.alert_channels.dingtalk.secret');
            if ($secret) {
                $timestamp = round(microtime(true) * 1000);
                $stringToSign = $timestamp . "\n" . $secret;
                $sign = urlencode(base64_pack('H*', hash_hmac('sha256', $stringToSign, $secret, true)));
                $webhook .= "&timestamp={$timestamp}&sign={$sign}";
            }

            Http::timeout(5)->post($webhook, [
                'msgtype' => 'markdown',
                'markdown' => [
                    'title' => '安防OA 告警',
                    'text'  => $message,
                ],
            ]);
        } catch (\Throwable $e) {
            Log::error('AlertService: dingtalk send failed', ['error' => $e->getMessage()]);
        }
    }

    private static function sendWechatWork(string $message, string $level): void
    {
        try {
            $webhook = config('monitoring.alert_channels.wechat_work.webhook');
            if (empty($webhook)) return;

            Http::timeout(5)->post($webhook, [
                'msgtype' => 'text',
                'text'    => [
                    'content' => $message,
                ],
            ]);
        } catch (\Throwable $e) {
            Log::error('AlertService: wechat_work send failed', ['error' => $e->getMessage()]);
        }
    }

    private static function sendMail(string $title, string $body): void
    {
        try {
            $to = config('monitoring.alert_channels.mail.to');
            if (empty($to)) return;

            // 使用 Laravel Mail facade 发送纯文本邮件
            // 需要配置 MAIL_* 环境变量
            Mail::raw($body, function ($message) use ($title, $to) {
                $message->to($to)->subject($title);
            });
        } catch (\Throwable $e) {
            Log::error('AlertService: mail send failed', ['error' => $e->getMessage()]);
        }
    }
}
