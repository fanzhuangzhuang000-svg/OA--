<?php

return [

    /*
    |--------------------------------------------------------------------------
    | 监控与告警配置 — 安防运维OA系统
    |--------------------------------------------------------------------------
    |
    | 此文件集中管理所有监控相关的阈值、渠道和开关。
    | 生产环境请通过 .env 覆盖敏感值（Sentry DSN、Webhook URL 等）。
    |
    */

    // ========== 健康检查 ==========
    'health' => [
        // 健康检查端点路径（公开，无需认证）
        'path' => '/api/health',

        // 各子项超时（秒）
        'db_timeout'    => 3,
        'cache_timeout' => 2,

        // 磁盘使用率告警阈值（百分比）
        'disk_warn_percent'  => 85,
        'disk_crit_percent'  => 95,
    ],

    // ========== 系统指标告警阈值 ==========
    'thresholds' => [
        // 数据库连接数
        'db_connections_warn'  => 80,
        'db_connections_crit'  => 150,

        // 慢查询数量（当前活跃）
        'slow_queries_warn'    => 3,
        'slow_queries_crit'    => 10,

        // 缓存命中率（低于此值告警）
        'cache_hit_rate_warn'  => 90.0,
        'cache_hit_rate_crit'  => 80.0,

        // 等待锁数量
        'waiting_locks_warn'   => 5,
        'waiting_locks_crit'   => 20,

        // 错误日志（24h 内）
        'errors_24h_warn'      => 50,
        'errors_24h_crit'      => 200,

        // 备份年龄（天）
        'backup_age_warn'      => 3,
        'backup_age_crit'      => 7,

        // 系统负载（1 分钟平均）
        'load_avg_warn'        => 4.0,
        'load_avg_crit'        => 8.0,
    ],

    // ========== 错误追踪 ==========
    'error_tracking' => [

        // Sentry 配置（推荐生产环境启用）
        'sentry' => [
            'enabled' => env('SENTRY_ENABLED', false),
            'dsn'     => env('SENTRY_DSN', ''),
            // 采样率: 1.0 = 100% 上报, 0.1 = 10%
            'traces_sample_rate' => env('SENTRY_TRACES_SAMPLE_RATE', 0.2),
            // 环境标识
            'environment' => env('APP_ENV', 'local'),
        ],

        // 本地错误日志配置
        'local' => [
            'channel'    => env('ERROR_LOG_CHANNEL', 'daily'),
            'days'       => env('ERROR_LOG_DAYS', 30),
            'json_lines' => true,  // JSON Lines 格式，方便 jq/awk 解析
        ],
    ],

    // ========== 告警通知渠道 ==========
    'alert_channels' => [

        // 飞书机器人 Webhook
        'feishu' => [
            'enabled' => env('ALERT_FEISHU_ENABLED', false),
            'webhook' => env('ALERT_FEISHU_WEBHOOK', ''),
        ],

        // 钉钉机器人 Webhook
        'dingtalk' => [
            'enabled' => env('ALERT_DINGTALK_ENABLED', false),
            'webhook' => env('ALERT_DINGTALK_WEBHOOK', ''),
            // 加签密钥（可选）
            'secret'  => env('ALERT_DINGTALK_SECRET', ''),
        ],

        // 企业微信机器人 Webhook
        'wechat_work' => [
            'enabled' => env('ALERT_WECHAT_WORK_ENABLED', false),
            'webhook' => env('ALERT_WECHAT_WORK_WEBHOOK', ''),
        ],

        // 邮件告警
        'mail' => [
            'enabled' => env('ALERT_MAIL_ENABLED', false),
            'to'      => env('ALERT_MAIL_TO', 'sre@example.com'),
        ],
    ],

    // ========== 监控数据采集 ==========
    'collection' => [
        // 指标采集间隔（秒），用于定时任务
        'interval' => env('MONITOR_INTERVAL', 60),

        // 指标保留天数
        'retention_days' => env('MONITOR_RETENTION_DAYS', 90),

        // 是否采集请求级指标（性能影响约 2-5%）
        'request_metrics' => env('MONITOR_REQUEST_METRICS', false),
    ],

];
