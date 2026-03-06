"""
Git Push 自动化工具

功能描述:
    自动将工作目录中的所有变更提交到 Git 仓库，并推送到远程分支
    
操作流程:
    1. 检查 Git 仓库状态
    2. 添加所有变更文件到暂存区
    3. 自动生成有意义的 commit message
    4. 执行 commit 操作
    5. 推送到远程仓库

适用场景:
    - 快速提交日常代码变更
    - 批量提交多个文件修改
    - 自动化部署流程中的代码同步
    - 团队协作中的频繁提交

输出信息:
    - Git 状态概览
    - 变更文件列表
    - Commit message
    - 推送结果

使用示例:
    python git_push_tool.py
    
注意事项:
    - 确保已经配置好 Git 用户信息
    - 确保有远程仓库的推送权限
    - 建议先检查变更内容再提交
    - 敏感文件应加入 .gitignore
"""


import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(command, check=True):
    """运行 shell 命令并返回结果"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=check,
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, "", str(e)


def check_git_status():
    """检查 Git 仓库状态"""
    print("🔍 检查 Git 仓库状态...")
    
    # 检查是否是 git 仓库
    success, stdout, stderr = run_command("git rev-parse --is-inside-work-tree")
    if not success:
        print("❌ 错误：当前目录不是 Git 仓库")
        return False
    
    # 获取工作状态
    success, stdout, stderr = run_command("git status --porcelain")
    if not stdout.strip():
        print("✅ 工作区干净，没有需要提交的变更")
        return False
    
    print(f"📝 发现变更:\n{stdout}")
    return True


def get_changed_files():
    """获取变更文件列表"""
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        return []
    
    files = []
    for line in stdout.strip().split('\n'):
        if line.strip():
            # 提取文件名（跳过状态码）
            file_path = line[3:].strip()
            files.append(file_path)
    
    return files


def generate_commit_message(files):
    """自动生成 commit message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 分析文件类型
    code_files = [f for f in files if f.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.h'))]
    config_files = [f for f in files if f.endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.env'))]
    doc_files = [f for f in files if f.endswith(('.md', '.txt', '.rst'))]
    other_files = [f for f in files if f not in code_files + config_files + doc_files]
    
    # 构建 commit message
    message_parts = [f"chore: auto-commit at {timestamp}"]
    message_parts.append("")
    
    if code_files:
        message_parts.append("Modified code files:")
        for f in code_files[:10]:  # 限制显示数量
            message_parts.append(f"  - {f}")
        if len(code_files) > 10:
            message_parts.append(f"  ... and {len(code_files) - 10} more")
    
    if config_files:
        message_parts.append("")
        message_parts.append("Updated configuration:")
        for f in config_files:
            message_parts.append(f"  - {f}")
    
    if doc_files:
        message_parts.append("")
        message_parts.append("Documentation changes:")
        for f in doc_files:
            message_parts.append(f"  - {f}")
    
    if other_files:
        message_parts.append("")
        message_parts.append("Other changes:")
        for f in other_files[:10]:
            message_parts.append(f"  - {f}")
        if len(other_files) > 10:
            message_parts.append(f"  ... and {len(other_files) - 10} more")
    
    return '\n'.join(message_parts)


def add_all_files():
    """添加所有变更到暂存区"""
    print("📦 添加所有变更文件到暂存区...")
    success, stdout, stderr = run_command("git add -A")
    if not success:
        print(f"❌ 添加文件失败：{stderr}")
        return False
    print("✅ 文件已成功添加到暂存区")
    return True


def commit_changes(message):
    """执行 commit 操作"""
    print("💾 提交变更...")
    
    # 使用 -F 参数从文件读取 commit message，避免转义问题
    temp_file = Path(".commit_message_temp.txt")
    temp_file.write_text(message, encoding='utf-8')
    
    success, stdout, stderr = run_command(f'git commit -F "{temp_file}"')
    
    # 清理临时文件
    temp_file.unlink(missing_ok=True)
    
    if not success:
        print(f"❌ 提交失败：{stderr}")
        return False
    
    print(f"✅ 成功提交:\n{message}")
    return True


def push_to_remote(branch=None):
    """推送到远程仓库"""
    if branch is None:
        # 获取当前分支
        success, stdout, stderr = run_command("git rev-parse --abbrev-ref HEAD")
        if success:
            branch = stdout.strip()
        else:
            branch = "main"
    
    print(f"🚀 推送到远程仓库 ({branch} 分支)...")
    success, stdout, stderr = run_command(f"git push origin {branch}")
    
    if not success:
        print(f"❌ 推送失败：{stderr}")
        return False
    
    print(f"✅ 成功推送到远程仓库")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("Git Push 自动化工具")
    print("=" * 60)
    print()
    
    # 1. 检查 Git 状态
    has_changes = check_git_status()
    if not has_changes:
        return 0
    
    # 2. 获取变更文件
    changed_files = get_changed_files()
    print(f"📊 共 {len(changed_files)} 个文件变更")
    
    # 3. 生成 commit message
    commit_msg = generate_commit_message(changed_files)
    
    # 4. 添加所有文件
    if not add_all_files():
        return 1
    
    # 5. 提交变更
    if not commit_changes(commit_msg):
        return 1
    
    # 6. 推送到远程
    if not push_to_remote():
        print("\n⚠️  提交成功但推送失败，请手动执行 git push")
        return 1
    
    print()
    print("=" * 60)
    print("✅ 所有操作完成!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
