# 告警与监控接入 (ALERTING)

## 当前状态
- 监控脚本: `/usr/local/bin/oa-monitor.sh` 每 5 分钟跑一次
- 告警落地: `/tmp/oa-alert-pending` (同一问题 30 分钟内不重复)
- 日志: `/var/log/oa-monitor.log`
- **告警通道: 占位,未接外部**

## 生产应接入

### 1. 企业微信机器人 (推荐)
在 `oa-monitor.sh` 中替换占位段:

```bash
WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"msgtype\":\"text\",\"text\":{\"content\":\"OA 告警: $(hostname) @ $TS - $report\"}}"
```

### 2. 钉钉机器人
```bash
WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"msgtype\":\"text\",\"text\":{\"content\":\"OA 告警: ...\"}}"
```

### 3. Alertmanager (Prometheus 生态)
- 暴露 `/metrics` (需 PHP-FPM exporter)
- Alertmanager 配 webhook 到企业微信/钉钉

### 4. Sentry
- Laravel 装 sentry-laravel,异常自动上报
- 配合 `LOG_LEVEL=error` + Sentry 阈值

## 自检

```bash
bash /usr/local/bin/oa-monitor.sh && tail -3 /var/log/oa-monitor.log
```

## 待办
- [ ] 创建企业微信群机器人,替换 WEBHOOK 占位
- [ ] 接入短信/电话 (PagerDuty 风格)
- [ ] 告警升级策略: 5 分钟没 ack 升级到 oncall
