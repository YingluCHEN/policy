#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
徐汇区政策URL验证工具
确保爬虫结果的真实性和可追溯性
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

class URLVerificationTool:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.verified_urls = []
        self.failed_urls = []

    def verify_single_url(self, url, policy_title=""):
        """验证单个URL的有效性"""
        try:
            print(f"验证: {policy_title[:60]}...")
            response = self.session.get(url, timeout=10)
            
            verification_result = {
                'url': url,
                'policy_title': policy_title,
                'status_code': response.status_code,
                'is_valid': response.status_code == 200,
                'content_length': len(response.content),
                'verification_time': datetime.now().isoformat(),
                'error': None
            }
            
            if response.status_code == 200:
                # 检查是否是徐汇区政府网站
                is_xuhui_gov = 'xuhui.gov.cn' in url
                
                # 检查内容是否包含关键信息
                content_text = response.text.lower()
                has_policy_content = any(keyword in content_text for keyword in [
                    '徐汇', '政策', '申报', '支持', '补贴', '人才', '企业'
                ])
                
                verification_result.update({
                    'is_xuhui_gov': is_xuhui_gov,
                    'has_policy_content': has_policy_content,
                    'quality_score': self.calculate_quality_score(content_text, url)
                })
                
                self.verified_urls.append(verification_result)
                print(f"  ✅ 有效 (状态码: {response.status_code}, 内容长度: {len(response.content)})")
            else:
                verification_result['error'] = f"HTTP {response.status_code}"
                self.failed_urls.append(verification_result)
                print(f"  ❌ 失效 (状态码: {response.status_code})")
                
        except Exception as e:
            verification_result = {
                'url': url,
                'policy_title': policy_title,
                'status_code': 0,
                'is_valid': False,
                'content_length': 0,
                'verification_time': datetime.now().isoformat(),
                'error': str(e),
                'is_xuhui_gov': 'xuhui.gov.cn' in url,
                'has_policy_content': False,
                'quality_score': 0
            }
            self.failed_urls.append(verification_result)
            print(f"  ❌ 失败 (错误: {str(e)})")
        
        return verification_result

    def calculate_quality_score(self, content_text, url):
        """计算URL内容质量评分"""
        score = 0
        
        # 基础分数
        if 'xuhui.gov.cn' in url:
            score += 20
        
        # 政策关键词
        policy_keywords = ['申报', '支持', '补贴', '奖励', '资助', '政策', '条件', '要求']
        for keyword in policy_keywords:
            if keyword in content_text:
                score += 5
        
        # 具体数额
        if any(term in content_text for term in ['万元', '亿元', '百万']):
            score += 10
        
        # 人才相关
        talent_keywords = ['人才', '博士', '硕士', '专家', '引进']
        for keyword in talent_keywords:
            if keyword in content_text:
                score += 3
        
        # AI相关
        ai_keywords = ['人工智能', 'ai', '算法', '大模型', '智能']
        for keyword in ai_keywords:
            if keyword in content_text:
                score += 3
        
        return min(score, 100)  # 最高100分

    def verify_from_json_file(self, json_file_path):
        """从JSON文件中读取政策数据并验证URL"""
        print(f"正在从 {json_file_path} 读取数据...")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            policies = data.get('policies', [])
            print(f"找到 {len(policies)} 个政策需要验证")
            
            # 并发验证URL
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_policy = {
                    executor.submit(self.verify_single_url, policy['url'], policy['title']): policy 
                    for policy in policies if 'url' in policy
                }
                
                for future in as_completed(future_to_policy):
                    try:
                        result = future.result()
                    except Exception as e:
                        print(f"验证过程中出错: {e}")
                    time.sleep(0.5)
                    
        except Exception as e:
            print(f"读取文件失败: {e}")
            return

    def verify_sample_urls(self):
        """验证一些样本URL"""
        sample_urls = [
            {
                'url': 'https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab0194a6f4d71614b0',
                'title': '徐汇区关于推动人工智能产业高质量发展的若干意见'
            },
            {
                'url': 'https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab0194a6f27fb814ac',
                'title': '徐汇区关于推动具身智能产业发展的若干意见'
            },
            {
                'url': 'https://www.xuhui.gov.cn/xxgk/portal/article/detail?id=8a4c0c0692292eab019384dc95a70aed',
                'title': '关于支持上海市生成式人工智能创新生态先导区的若干措施'
            },
            {
                'url': 'https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=1',
                'title': '徐汇区科委政策列表页面'
            },
            {
                'url': 'https://www.xuhui.gov.cn',
                'title': '徐汇区政府官网首页'
            }
        ]
        
        print("验证样本URL...")
        for sample in sample_urls:
            self.verify_single_url(sample['url'], sample['title'])
            time.sleep(1)

    def generate_verification_report(self):
        """生成验证报告"""
        os.makedirs('data', exist_ok=True)
        
        total_urls = len(self.verified_urls) + len(self.failed_urls)
        valid_count = len(self.verified_urls)
        invalid_count = len(self.failed_urls)
        
        # 统计分析
        quality_scores = [url['quality_score'] for url in self.verified_urls if 'quality_score' in url]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # 生成详细报告
        report_content = f"""
# 徐汇区政策URL验证报告

## 验证概览
- **验证时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **总URL数量**: {total_urls}
- **有效URL数量**: {valid_count} ({valid_count/total_urls*100:.1f}%)
- **失效URL数量**: {invalid_count} ({invalid_count/total_urls*100:.1f}%)
- **平均质量评分**: {avg_quality:.1f}/100

## 验证结果详情

### ✅ 有效URL ({valid_count}个)
"""
        
        for i, url_info in enumerate(self.verified_urls, 1):
            report_content += f"""
**{i}. {url_info['policy_title']}**
- URL: {url_info['url']}
- 状态码: {url_info['status_code']}
- 内容长度: {url_info['content_length']} 字节
- 质量评分: {url_info.get('quality_score', 0)}/100
- 验证时间: {url_info['verification_time']}
"""

        if self.failed_urls:
            report_content += f"\n### ❌ 失效URL ({invalid_count}个)\n"
            for i, url_info in enumerate(self.failed_urls, 1):
                report_content += f"""
**{i}. {url_info['policy_title']}**
- URL: {url_info['url']}
- 错误信息: {url_info['error']}
- 验证时间: {url_info['verification_time']}
"""

        # 保存报告
        with open('data/url_verification_report.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # 导出验证数据
        all_results = self.verified_urls + self.failed_urls
        
        # JSON格式
        with open('data/url_verification_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'verification_time': datetime.now().isoformat(),
                'summary': {
                    'total_urls': total_urls,
                    'valid_urls': valid_count,
                    'invalid_urls': invalid_count,
                    'success_rate': valid_count/total_urls*100 if total_urls > 0 else 0,
                    'average_quality_score': avg_quality
                },
                'results': all_results
            }, f, ensure_ascii=False, indent=2)
        
        # CSV格式
        df = pd.DataFrame(all_results)
        df.to_csv('data/url_verification_results.csv', index=False, encoding='utf-8-sig')
        
        print(f"\n📊 验证报告已生成:")
        print(f"   📋 详细报告: data/url_verification_report.md")
        print(f"   📊 验证数据: data/url_verification_results.json")
        print(f"   📊 表格数据: data/url_verification_results.csv")
        print(f"\n✅ URL有效率: {valid_count}/{total_urls} ({valid_count/total_urls*100:.1f}%)")
        print(f"📈 平均质量评分: {avg_quality:.1f}/100")

def main():
    print("🔍 徐汇区政策URL验证工具")
    print("=" * 50)
    
    verifier = URLVerificationTool()
    
    # 选择验证模式
    print("请选择验证模式:")
    print("1. 验证样本URL (推荐)")
    print("2. 验证JSON文件中的所有URL")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        verifier.verify_sample_urls()
    elif choice == "2":
        json_files = [
            'data/enhanced_talent_policies.json',
            'data/comprehensive_talent_policies.json',
            'data/talent_policies.json'
        ]
        
        available_files = [f for f in json_files if os.path.exists(f)]
        
        if available_files:
            print(f"找到以下数据文件:")
            for i, file in enumerate(available_files, 1):
                print(f"  {i}. {file}")
            
            file_choice = input("请选择文件编号: ").strip()
            try:
                selected_file = available_files[int(file_choice) - 1]
                verifier.verify_from_json_file(selected_file)
            except (ValueError, IndexError):
                print("无效选择，使用默认文件")
                verifier.verify_from_json_file(available_files[0])
        else:
            print("未找到数据文件，改为验证样本URL")
            verifier.verify_sample_urls()
    else:
        print("无效选择，使用样本URL验证")
        verifier.verify_sample_urls()
    
    # 生成报告
    verifier.generate_verification_report()

if __name__ == "__main__":
    main() 