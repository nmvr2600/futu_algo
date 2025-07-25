#!/usr/bin/env python3
"""
缠论测试运行器
统一运行所有缠论测试套件
"""

import sys
import os
import subprocess
import argparse
from typing import Dict, List
import time

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRunner:
    """测试运行器类"""

    def __init__(self):
        self.test_files = [
            "test_chanlun_core_features.py",
            "test_chanlun_strokes_segments.py",
            "test_chanlun_central_mapping.py",
            "test_chanlun_comprehensive.py",
        ]
        self.test_dir = os.path.dirname(os.path.abspath(__file__))

    def run_single_test(self, test_file: str, verbose: bool = False) -> Dict:
        """运行单个测试文件"""
        test_path = os.path.join(self.test_dir, test_file)

        if not os.path.exists(test_path):
            return {
                "file": test_file,
                "success": False,
                "output": f"文件不存在: {test_path}",
                "duration": 0,
            }

        print(f"\n{'='*80}")
        print(f"运行测试: {test_file}")
        print("=" * 80)

        start_time = time.time()

        try:
            # 构建命令
            cmd = [sys.executable, test_path]
            if verbose:
                cmd.append("-v")

            # 运行测试
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.test_dir
            )

            duration = time.time() - start_time

            success = result.returncode == 0

            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr

            return {
                "file": test_file,
                "success": success,
                "output": output,
                "duration": duration,
                "returncode": result.returncode,
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "file": test_file,
                "success": False,
                "output": str(e),
                "duration": duration,
                "error": str(e),
            }

    def run_all_tests(self, verbose: bool = False) -> Dict:
        """运行所有测试"""
        print("🚀 开始运行缠论测试套件...")
        print(f"测试目录: {self.test_dir}")

        results = {}
        total_start = time.time()

        for test_file in self.test_files:
            results[test_file] = self.run_single_test(test_file, verbose)

        total_duration = time.time() - total_start

        return {"results": results, "total_duration": total_duration}

    def generate_report(self, results: Dict[str, Dict]) -> str:
        """生成测试报告"""
        report = []
        report.append("=" * 80)
        report.append("缠论测试套件运行报告")
        report.append("=" * 80)

        passed = 0
        failed = 0

        for test_file, result in results["results"].items():
            if result["success"]:
                passed += 1
                status = "✅ 通过"
            else:
                failed += 1
                status = "❌ 失败"

            report.append(f"\n{status} {test_file}")
            report.append(f"  耗时: {result['duration']:.2f}秒")

            if not result["success"]:
                report.append(f"  错误: {result.get('output', '未知错误')}")

        report.append("\n" + "=" * 80)
        report.append("总结:")
        report.append(f"  总测试数: {len(results['results'])}")
        report.append(f"  通过数: {passed}")
        report.append(f"  失败数: {failed}")
        report.append(f"  通过率: {passed/len(results['results'])*100:.1f}%")
        report.append(f"  总耗时: {results['total_duration']:.2f}秒")

        return "\n".join(report)

    def run_specific_test(self, test_name: str, verbose: bool = False) -> Dict:
        """运行特定测试"""
        if not test_name.endswith(".py"):
            test_name += ".py"

        if test_name not in self.test_files:
            available = "\n".join(f"  - {f}" for f in self.test_files)
            return {
                "error": f"测试文件不存在: {test_name}",
                "available_files": available,
            }

        return self.run_single_test(test_name, verbose)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="缠论测试运行器")
    parser.add_argument("test_file", nargs="?", help="指定测试文件运行 (可选)")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("-r", "--report", action="store_true", help="生成详细报告")

    args = parser.parse_args()

    runner = TestRunner()

    if args.test_file:
        # 运行特定测试
        result = runner.run_specific_test(args.test_file, args.verbose)

        if "error" in result:
            print(f"❌ {result['error']}")
            if "available_files" in result:
                print("可用测试文件:")
                print(result["available_files"])
            return 1

        print(
            runner.generate_report(
                {
                    "results": {args.test_file: result},
                    "total_duration": result["duration"],
                }
            )
        )

    else:
        # 运行所有测试
        results = runner.run_all_tests(args.verbose)
        report = runner.generate_report(results)
        print(report)

        # 返回适当的退出码
        failed_count = sum(1 for r in results["results"].values() if not r["success"])
        return 0 if failed_count == 0 else 1

    return 0


if __name__ == "__main__":
    exit(main())
