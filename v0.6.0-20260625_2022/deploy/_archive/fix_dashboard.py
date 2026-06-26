#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix DashboardController missing imports"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('172.20.0.139', username='nbcy', password='admin123', timeout=10)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(f'echo admin123 | sudo -S {cmd}', timeout=30)
    return stdout.read().decode('utf-8', errors='replace').strip()

# Add missing imports to ModuleControllers.php
run('chown nbcy:nbcy /var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php')

sftp = ssh.open_sftp()
content = sftp.open('/var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php').read().decode('utf-8')

# Add missing model imports
old_import = "use App\\Models\\{Customer, CustomerContact, FollowUpRecord, CustomerDevice, User, Department, Position, EmployeeProfile, SkillTag, Certificate, ExpenseClaim, ExpenseItem, Vehicle, VehicleInsurance, VehicleMaintenanceRecord, VehicleUsageRequest, Warehouse, InventoryItem, StockRecord, DeviceSerialNumber, Receivable, Payable, DiskFolder, DiskFile, KnowledgeCategory, KnowledgeArticle};"

new_import = "use App\\Models\\{Customer, CustomerContact, FollowUpRecord, CustomerDevice, User, Department, Position, EmployeeProfile, SkillTag, Certificate, ExpenseClaim, ExpenseItem, Vehicle, VehicleInsurance, VehicleMaintenanceRecord, VehicleUsageRequest, Warehouse, InventoryItem, StockRecord, DeviceSerialNumber, Receivable, Payable, DiskFolder, DiskFile, KnowledgeCategory, KnowledgeArticle, Project, ServiceOrder, AttendanceRecord, LeaveRequest, OvertimeRequest, ApprovalRecord};"

content = content.replace(old_import, new_import)

sftp.open('/var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php', 'w').write(content)
sftp.close()

run('chown www-data:www-data /var/www/oa-api/app/Http/Controllers/Api/ModuleControllers.php')

# Clear caches
run('php /var/www/oa-api/artisan config:clear')
run('php /var/www/oa-api/artisan cache:clear')
print("Fixed and caches cleared")

ssh.close()
