"""debug 401 问题：单端点单独测 vs 串行批量测对比"""
import sys
sys.path.insert(0, '.workbuddy')
from ssh_helper import ssh_exec, ssh_exec_password  # 找现有 helper
