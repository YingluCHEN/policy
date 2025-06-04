#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
徐汇区人才政策爬虫
重点提取企业申报要求
"""

import requests
import re
import json
import time
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
import os

class XuhuiTalentCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 徐汇区政府网站URLs - 重点关注人才政策
        self.urls = [
            # 政务公开 - 政策文件
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=2",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=3",
            # 人力资源和社会保障局
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=2",
            # 科学技术委员会
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=2",
            # 商务委员会
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_sww&page=1",
            # 发展和改革委员会
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_fgw&page=1",
            # 徐汇区政府主站搜索人才相关
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=人才",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=AI",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=人工智能",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=创业",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=科技"
        ]
        
        # 人才政策关键词
        self.talent_keywords = [
            "人才", "高层次", "领军", "专家", "博士", "硕士", "海外", "引进",
            "创业", "孵化", "科技", "研发", "创新", "AI", "人工智能", "智能",
            "补贴", "资助", "奖励", "扶持", "资金", "支持", "专项",
            "申报", "申请", "条件", "要求", "材料", "截止", "期限"
        ]
        
        # 企业申报要求关键词
        self.application_keywords = {
            "企业要求": ["注册地", "注册资本", "营业收入", "纳税", "规模", "行业", "资质", "成立时间", "高新技术企业", "独角兽", "从业人员"],
            "申报条件": ["申报条件", "基本条件", "准入条件", "资格条件", "学历要求", "工作经验", "年龄限制", "专业背景"],
            "申报材料": ["申报材料", "申请材料", "证明材料", "附件", "申请表", "推荐信", "简历", "学历证明", "工作证明"],
            "申报时间": ["截止时间", "申报时间", "申报期间", "受理时间", "办理时限", "有效期", "评审时间", "公示时间"]
        }
        
        self.policies = []

    def fetch_page(self, url):
        """获取页面内容"""
        try:
            print(f"正在爬取: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"获取页面失败 {url}: {e}")
            return None

    def extract_policy_links(self, html, base_url):
        """从列表页提取政策链接"""
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # 查找所有可能的政策链接
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            title = a.get_text(strip=True)
            
            # 检查是否是人才相关政策
            if any(keyword in title for keyword in self.talent_keywords):
                full_url = urljoin(base_url, href)
                links.append({
                    'title': title,
                    'url': full_url
                })
        
        return links

    def extract_policy_content(self, url):
        """提取政策详细内容"""
        html = self.fetch_page(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title = ""
        title_selectors = ['h1', '.title', '.art-title', '[class*="title"]']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                break
        
        # 提取内容
        content = ""
        content_selectors = ['.content', '.art-content', '[class*="content"]', '.main', 'article']
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text(strip=True)
                break
        
        # 如果没找到特定的内容区域，取body内容
        if not content:
            body = soup.find('body')
            if body:
                content = body.get_text(strip=True)
        
        # 提取发布时间
        publish_date = ""
        date_patterns = [
            r'(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?)',
            r'(\d{4}/\d{1,2}/\d{1,2})',
            r'(\d{4}\.\d{1,2}\.\d{1,2})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, content + title)
            if match:
                publish_date = match.group(1)
                break
        
        # 提取发布部门
        department = ""
        dept_keywords = ["徐汇区", "上海市", "人力资源", "科技", "发改", "商务", "房管", "教育"]
        for keyword in dept_keywords:
            if keyword in content or keyword in title:
                # 尝试提取包含关键词的部门名称
                dept_match = re.search(f'({keyword}[^，。；！？\n]*?[局|委|办|中心|部])', content + title)
                if dept_match:
                    department = dept_match.group(1)
                    break
        
        return {
            'title': title,
            'url': url,
            'content': content[:2000],  # 限制内容长度
            'publish_date': publish_date,
            'department': department,
            'crawl_time': datetime.now().isoformat()
        }

    def classify_policy(self, policy):
        """政策分类"""
        text = f"{policy['title']} {policy['content']}"
        
        categories = {
            "人才引进": ["人才引进", "海外人才", "高层次人才", "领军人才", "专家", "院士", "千人计划"],
            "AI/人工智能": ["AI", "人工智能", "智能", "算法", "机器学习", "深度学习", "大模型", "生成式AI"],
            "创业扶持": ["创业", "孵化", "初创", "创新创业", "双创", "创客", "众创空间"],
            "资金补贴": ["补贴", "资助", "奖励", "资金支持", "专项资金", "扶持资金"],
            "住房保障": ["住房", "租房", "购房", "安居", "人才公寓", "住房补贴"],
            "子女教育": ["子女", "教育", "入学", "就学", "学校", "教育优惠"],
            "医疗保障": ["医疗", "健康", "就医", "体检", "医疗服务"],
            "落户服务": ["落户", "户籍", "居住证", "积分", "迁户"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "其他"

    def extract_application_requirements(self, policy):
        """提取企业申报要求"""
        text = f"{policy['title']} {policy['content']}"
        requirements = {}
        
        for req_type, keywords in self.application_keywords.items():
            found_requirements = []
            
            for keyword in keywords:
                # 查找包含关键词的句子
                sentences = re.split(r'[。！？\n]', text)
                for sentence in sentences:
                    if keyword in sentence and len(sentence.strip()) > 10:
                        cleaned = sentence.strip()
                        if cleaned and len(cleaned) > 5:
                            found_requirements.append(cleaned)
            
            # 去重并限制数量
            unique_requirements = list(dict.fromkeys(found_requirements))[:3]
            requirements[req_type] = "; ".join(unique_requirements) if unique_requirements else ""
        
        return requirements

    def crawl_all_policies(self):
        """爬取所有政策"""
        print("开始爬取徐汇区人才政策...")
        
        # 创建输出目录
        os.makedirs('data', exist_ok=True)
        
        all_links = []
        
        # 从各个页面收集政策链接
        for url in self.urls:
            html = self.fetch_page(url)
            if html:
                links = self.extract_policy_links(html, url)
                all_links.extend(links)
            time.sleep(1)  # 爬取间隔
        
        # 去重
        unique_links = []
        seen_urls = set()
        for link in all_links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        print(f"找到 {len(unique_links)} 个人才相关政策链接")
        
        # 提取每个政策的详细内容
        for i, link in enumerate(unique_links[:20], 1):  # 限制爬取数量
            print(f"正在处理第 {i} 个政策: {link['title'][:50]}...")
            
            policy = self.extract_policy_content(link['url'])
            if policy and len(policy['content']) > 100:  # 过滤掉内容太少的页面
                policy['category'] = self.classify_policy(policy)
                policy['application_requirements'] = self.extract_application_requirements(policy)
                self.policies.append(policy)
            
            time.sleep(2)  # 爬取间隔
        
        print(f"成功爬取 {len(self.policies)} 个政策")

    def analyze_and_export(self):
        """分析数据并导出"""
        if not self.policies:
            print("没有爬取到有效数据")
            return
        
        print("正在分析数据...")
        
        # 统计分析
        categories = {}
        departments = {}
        policies_with_requirements = 0
        
        for policy in self.policies:
            # 分类统计
            cat = policy.get('category', '其他')
            categories[cat] = categories.get(cat, 0) + 1
            
            # 部门统计
            dept = policy.get('department', '未知')
            departments[dept] = departments.get(dept, 0) + 1
            
            # 申报要求统计
            req = policy.get('application_requirements', {})
            if any(v.strip() for v in req.values() if v):
                policies_with_requirements += 1
        
        # 导出JSON格式
        output_data = {
            'crawl_time': datetime.now().isoformat(),
            'total_policies': len(self.policies),
            'statistics': {
                'categories': categories,
                'departments': departments,
                'policies_with_requirements': policies_with_requirements
            },
            'policies': self.policies
        }
        
        with open('data/talent_policies.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # 导出CSV格式
        df_data = []
        for policy in self.policies:
            req = policy.get('application_requirements', {})
            df_data.append({
                '标题': policy.get('title', ''),
                '分类': policy.get('category', ''),
                '发布部门': policy.get('department', ''),
                '发布时间': policy.get('publish_date', ''),
                '链接': policy.get('url', ''),
                '企业要求': req.get('企业要求', ''),
                '申报条件': req.get('申报条件', ''),
                '申报材料': req.get('申报材料', ''),
                '申报时间': req.get('申报时间', ''),
                '内容摘要': policy.get('content', '')[:200]
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv('data/talent_policies.csv', index=False, encoding='utf-8-sig')
        df.to_excel('data/talent_policies.xlsx', index=False)
        
        # 导出企业申报要求汇总
        with open('data/application_requirements.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("徐汇区人才政策企业申报要求汇总\n")
            f.write("=" * 60 + "\n\n")
            
            for i, policy in enumerate(self.policies, 1):
                req = policy.get('application_requirements', {})
                has_req = any(v.strip() for v in req.values() if v)
                
                if has_req:
                    f.write(f"{i}. 【{policy.get('category', '其他')}】{policy.get('title', '')}\n")
                    f.write(f"   发布部门: {policy.get('department', '未知')}\n")
                    f.write(f"   发布时间: {policy.get('publish_date', '未知')}\n")
                    f.write(f"   链接: {policy.get('url', '')}\n")
                    
                    for req_type, req_content in req.items():
                        if req_content.strip():
                            f.write(f"   {req_type}: {req_content}\n")
                    f.write("\n" + "-" * 60 + "\n\n")
        
        # 生成分析报告
        with open('data/analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write("徐汇区人才政策分析报告\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总政策数量: {len(self.policies)} 条\n")
            f.write(f"包含申报要求的政策: {policies_with_requirements} 条\n\n")
            
            f.write("政策分类分布:\n")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                percentage = count / len(self.policies) * 100
                f.write(f"  {cat}: {count}条 ({percentage:.1f}%)\n")
            
            f.write(f"\n主要发布部门:\n")
            for dept, count in sorted(departments.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {dept}: {count}条\n")
        
        print(f"\n数据已导出到 data/ 目录:")
        print(f"- 详细数据: data/talent_policies.json")
        print(f"- 表格数据: data/talent_policies.csv")
        print(f"- Excel文件: data/talent_policies.xlsx")
        print(f"- 申报要求: data/application_requirements.txt")
        print(f"- 分析报告: data/analysis_report.txt")

def main():
    crawler = XuhuiTalentCrawler()
    crawler.crawl_all_policies()
    crawler.analyze_and_export()
    
    print("\n🎯 爬取完成！重点关注以下文件:")
    print("📋 企业申报要求: data/application_requirements.txt")
    print("📊 分析报告: data/analysis_report.txt")

if __name__ == "__main__":
    main() 