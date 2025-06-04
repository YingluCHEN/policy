#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
徐汇区企业人才政策综合爬虫
覆盖更全面的政策来源，重点关注企业申报要求
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
from concurrent.futures import ThreadPoolExecutor, as_completed

class ComprehensiveTalentCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 更全面的徐汇区人才政策URL
        self.urls = [
            # 徐汇区政府主站 - 政策法规
            "https://www.xuhui.gov.cn/zcfg/",
            "https://www.xuhui.gov.cn/zcfg/sfxwj/",
            "https://www.xuhui.gov.cn/zcfg/qfxwj/",
            
            # 政务公开 - 规范性文件
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_zcwj",
            
            # 人力资源和社会保障局
            "https://www.xuhui.gov.cn/renshebao/",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj",
            
            # 住房保障和房屋管理局
            "https://www.xuhui.gov.cn/fangtuju/",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_zfbzj",
            
            # 科学技术委员会
            "https://www.xuhui.gov.cn/kejiju/",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw",
            
            # 教育局
            "https://www.xuhui.gov.cn/jiaoyu/",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_jyj",
            
            # 发展和改革委员会
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_fgw",
            
            # 商务委员会
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_sww",
            
            # 通知公告
            "https://www.xuhui.gov.cn/tzgg/",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_gggs",
            
            # 直接搜索人才政策相关页面
            "https://www.xuhui.gov.cn/ztlm/",  # 专题专栏
            "https://www.xuhui.gov.cn/zdly/",  # 重点领域
            
            # 徐汇区新型工业化推进办公室
            "https://www.xuhui.gov.cn/xgybgs/",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xgybgs",
            
            # 更多的政策页面
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=2",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=3",
        ]
        
        # 更详细的人才关键词
        self.talent_keywords = [
            # 直接人才政策
            "人才政策", "人才服务", "人才计划", "人才工程", "人才项目",
            "人才引进", "人才招聘", "人才培养", "人才评价", "人才激励",
            
            # 高端人才
            "高层次人才", "领军人才", "拔尖人才", "骨干人才", "青年人才",
            "海外人才", "外籍人才", "国际人才", "留学人员", "海归",
            
            # 学历职称
            "博士", "硕士", "教授", "研究员", "高级工程师", "专家",
            "院士", "学者", "科学家", "技术人员", "研发人员",
            
            # 人才计划
            "千人计划", "万人计划", "杰青", "长江学者", "博士后",
            "优秀人才", "紧缺人才", "特殊人才", "创新人才", "创业人才",
            
            # 住房相关
            "人才公寓", "人才房", "住房补贴", "租房补贴", "购房补贴",
            "住房支持", "住房优惠", "安居工程", "保障性住房", "公租房",
            "廉租房", "租赁住房", "住房保障", "租金补贴", "房租补助",
            
            # 落户相关
            "人才落户", "直接落户", "落户政策", "户籍政策", "居住证",
            "积分落户", "居住证积分", "户口迁移", "户籍管理",
            
            # 子女教育
            "子女入学", "子女教育", "教育优惠", "入学政策", "择校",
            "教育服务", "学区", "国际学校", "优质教育资源",
            
            # 配套服务
            "医疗保障", "医疗服务", "健康服务", "配偶就业", "家属安置",
            "绿色通道", "一站式服务", "人才服务中心", "人才驿站",
            
            # 资金支持
            "人才资助", "人才补贴", "人才奖励", "创业补贴", "科研资助",
            "项目资助", "启动资金", "津贴", "安家费", "生活补贴",
            
            # 企业人才
            "企业人才", "用人单位", "人才引进企业", "雇主", "招聘单位"
        ]
        
        # 企业申报条件关键词
        self.company_keywords = [
            "企业注册", "注册地", "注册资本", "营业执照", "经营期限",
            "企业性质", "行业类别", "经营范围", "纳税", "信用",
            "高新技术企业", "专精特新", "规模以上", "上市公司",
            "申报条件", "申请条件", "申报要求", "申报材料", "申报流程",
            "企业要求", "用人单位条件", "雇主条件", "招聘企业"
        ]
        
        self.policies = []

    def fetch_page(self, url):
        """获取页面内容"""
        try:
            print(f"正在爬取: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"获取页面失败 {url}: {e}")
            return None

    def extract_links_from_page(self, html, base_url):
        """从页面提取相关链接"""
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # 多种链接选择器
        selectors = [
            'a[href*="detail"]',
            'a[href*="article"]',
            'a[href*="policy"]',
            'a[href*="talent"]',
            'a[href*="人才"]',
            '.list-item a',
            '.title a',
            '.policy-title a',
            '.news-title a',
            'li a',
            '.content a'
        ]
        
        found_links = []
        for selector in selectors:
            found_links.extend(soup.select(selector))
        
        # 过滤和识别人才相关链接
        seen_hrefs = set()
        for a in found_links:
            href = a.get('href')
            title = a.get_text(strip=True)
            
            if href and href not in seen_hrefs and len(title) > 3:
                # 检查是否与人才相关
                is_talent_related = (
                    any(keyword in title for keyword in self.talent_keywords) or
                    any(keyword in title for keyword in self.company_keywords) or
                    '人才' in title or '住房' in title or '落户' in title or 
                    '博士' in title or '硕士' in title or '专家' in title or
                    '引进' in title or '补贴' in title or '公寓' in title
                )
                
                if is_talent_related:
                    full_url = urljoin(base_url, href)
                    links.append({
                        'title': title,
                        'url': full_url
                    })
                    seen_hrefs.add(href)
        
        return links

    def extract_content_from_url(self, url):
        """从URL提取内容"""
        html = self.fetch_page(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title = ""
        title_selectors = [
            'h1', 'h2', 'h3', '.title', '.art-title', '.page-title',
            '[class*="title"]', '[class*="head"]', '.main-title', '.news-title'
        ]
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem:
                candidate_title = elem.get_text(strip=True)
                if len(candidate_title) > 5 and len(candidate_title) < 200:
                    title = candidate_title
                    break
        
        # 提取内容
        content = ""
        content_selectors = [
            '.content', '.art-content', '.main-content', '.policy-content',
            '[class*="content"]', '.main', 'article', '.detail', '.text', '.body'
        ]
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                # 移除导航等无关元素
                for nav in elem.select('nav, .nav, .menu, .breadcrumb, .pagination, .sidebar'):
                    nav.decompose()
                content = elem.get_text(strip=True)
                if len(content) > 200:
                    break
        
        if not content or len(content) < 100:
            body = soup.find('body')
            if body:
                for elem in body.select('nav, .nav, .menu, .sidebar, .footer, .header, .breadcrumb'):
                    elem.decompose()
                content = body.get_text(strip=True)
        
        # 提取时间
        publish_date = ""
        date_patterns = [
            r'(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?)',
            r'(\d{4}/\d{1,2}/\d{1,2})',
            r'(\d{4}\.\d{1,2}\.\d{1,2})',
            r'发布时间[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2})',
            r'时间[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content + title)
            if match:
                publish_date = match.group(1)
                break
        
        # 提取部门
        department = ""
        dept_patterns = [
            r'发布机构[：:]\s*([^，。；！？\n]+)',
            r'发布部门[：:]\s*([^，。；！？\n]+)',
            r'(徐汇区[^，。；！？\n]*?[局|委|办|中心|部|处])',
            r'(上海市徐汇区[^，。；！？\n]*?[局|委|办|中心|部|处])'
        ]
        
        for pattern in dept_patterns:
            match = re.search(pattern, content + title)
            if match:
                department = match.group(1).strip()
                break
        
        return {
            'title': title,
            'url': url,
            'content': content[:8000],  # 增加内容长度
            'publish_date': publish_date,
            'department': department,
            'crawl_time': datetime.now().isoformat()
        }

    def classify_policy(self, policy):
        """政策分类"""
        text = f"{policy['title']} {policy['content']}"
        
        categories = {
            "人才引进": [
                "人才引进", "人才招聘", "海外人才", "高层次人才", "领军人才",
                "专家引进", "博士引进", "硕士引进", "人才计划", "千人计划"
            ],
            "住房保障": [
                "住房补贴", "房屋补贴", "租房补贴", "人才公寓", "住房支持",
                "保障性住房", "公租房", "廉租房", "安居", "租金", "住房优惠"
            ],
            "落户服务": [
                "落户", "户籍", "居住证", "积分", "迁户", "户口", "落户政策"
            ],
            "子女教育": [
                "子女入学", "子女教育", "教育优惠", "入学", "学区", "择校"
            ],
            "创业扶持": [
                "创业支持", "创业补贴", "创业孵化", "创业基金", "初创", "众创"
            ],
            "资金资助": [
                "人才资助", "人才奖励", "科研资助", "项目资助", "津贴", "补助", "安家费"
            ],
            "医疗服务": [
                "医疗保障", "医疗服务", "健康", "体检", "医疗优惠", "就医"
            ]
        }
        
        # 计算得分
        category_scores = {}
        for category, keywords in categories.items():
            score = 0
            for keyword in keywords:
                if keyword in policy['title']:
                    score += 3
                if keyword in policy['content']:
                    score += 1
            category_scores[category] = score
        
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return "其他"

    def extract_company_requirements(self, policy):
        """提取企业申报要求"""
        text = f"{policy['title']} {policy['content']}"
        
        # 企业要求关键词分类
        requirement_patterns = {
            "企业基本条件": [
                "注册地", "注册资本", "实缴资本", "营业执照", "经营期限",
                "企业性质", "行业类别", "经营范围", "纳税", "信用记录",
                "高新技术企业", "专精特新", "规模以上企业", "上市公司"
            ],
            "人才要求": [
                "学历要求", "学位要求", "专业要求", "工作经验", "年龄限制",
                "技术职称", "专业技能", "海外经历", "获奖情况", "学术成果"
            ],
            "申报材料": [
                "申报表", "申请表", "身份证明", "学历证明", "工作证明",
                "推荐信", "简历", "业绩材料", "获奖证书", "专利证书"
            ],
            "申报时间": [
                "申报时间", "截止时间", "受理期间", "评审时间", "公示时间",
                "办理时限", "有效期", "年度申报", "常年受理"
            ],
            "支持标准": [
                "补贴标准", "奖励金额", "支持额度", "最高限额", "一次性",
                "按年度", "分期拨付", "配套资金", "专项资金"
            ]
        }
        
        requirements = {}
        for req_type, keywords in requirement_patterns.items():
            found_items = []
            
            # 按句子分割并搜索
            sentences = re.split(r'[。！？；\n]', text)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 15 and len(sentence) < 500:
                    for keyword in keywords:
                        if keyword in sentence:
                            # 过滤无效句子
                            if not sentence.startswith(('首页', '返回', '上一页', '下一页', '点击')):
                                found_items.append(sentence)
                                break
            
            # 去重并限制数量
            unique_items = []
            seen = set()
            for item in found_items:
                if item not in seen:
                    unique_items.append(item)
                    seen.add(item)
                if len(unique_items) >= 5:
                    break
            
            requirements[req_type] = "; ".join(unique_items) if unique_items else ""
        
        return requirements

    def crawl_policies(self):
        """爬取政策"""
        print("开始全面爬取徐汇区企业人才政策...")
        print(f"将爬取 {len(self.urls)} 个政策源")
        
        os.makedirs('data', exist_ok=True)
        
        all_links = []
        
        # 第一步：从各个页面收集链接
        for url in self.urls:
            html = self.fetch_page(url)
            if html:
                links = self.extract_links_from_page(html, url)
                all_links.extend(links)
                if links:
                    print(f"从 {url} 获取到 {len(links)} 个相关链接")
            time.sleep(1)
        
        # 第二步：去重
        unique_links = []
        seen_urls = set()
        for link in all_links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        print(f"去重后共找到 {len(unique_links)} 个人才相关链接")
        
        # 第三步：提取详细内容（增加到80个）
        target_links = unique_links[:80]
        print(f"将详细爬取前 {len(target_links)} 个政策")
        
        for i, link in enumerate(target_links, 1):
            print(f"正在处理第 {i}/{len(target_links)} 个: {link['title'][:50]}...")
            
            policy = self.extract_content_from_url(link['url'])
            if policy and len(policy['content']) > 200:
                policy['category'] = self.classify_policy(policy)
                policy['company_requirements'] = self.extract_company_requirements(policy)
                
                # 过滤：只保留有实际内容的政策
                has_meaningful_content = (
                    len(policy['content']) > 500 or
                    any(len(v.strip()) > 20 for v in policy['company_requirements'].values() if v) or
                    any(keyword in policy['title'] + policy['content'] for keyword in 
                        ['人才', '住房', '落户', '博士', '硕士', '补贴', '公寓', '引进'])
                )
                
                if has_meaningful_content:
                    self.policies.append(policy)
                    print(f"  ✅ 已保存 (分类: {policy['category']})")
                else:
                    print(f"  ❌ 跳过 (内容不足)")
            
            time.sleep(1)
        
        print(f"\n🎯 成功爬取 {len(self.policies)} 个人才政策")

    def export_results(self):
        """导出结果"""
        if not self.policies:
            print("没有数据可导出")
            return
        
        print("正在导出数据...")
        
        # 统计
        categories = {}
        departments = {}
        for policy in self.policies:
            cat = policy.get('category', '其他')
            categories[cat] = categories.get(cat, 0) + 1
            
            dept = policy.get('department', '未知')
            departments[dept] = departments.get(dept, 0) + 1
        
        # JSON导出
        output_data = {
            'crawl_time': datetime.now().isoformat(),
            'total_policies': len(self.policies),
            'categories': categories,
            'departments': departments,
            'policies': self.policies
        }
        
        with open('data/comprehensive_talent_policies.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # Excel导出
        df_data = []
        for policy in self.policies:
            req = policy.get('company_requirements', {})
            df_data.append({
                '标题': policy.get('title', ''),
                '分类': policy.get('category', ''),
                '发布部门': policy.get('department', ''),
                '发布时间': policy.get('publish_date', ''),
                '链接': policy.get('url', ''),
                '企业基本条件': req.get('企业基本条件', ''),
                '人才要求': req.get('人才要求', ''),
                '申报材料': req.get('申报材料', ''),
                '申报时间': req.get('申报时间', ''),
                '支持标准': req.get('支持标准', ''),
                '内容摘要': policy.get('content', '')[:500]
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv('data/comprehensive_talent_policies.csv', index=False, encoding='utf-8-sig')
        df.to_excel('data/comprehensive_talent_policies.xlsx', index=False)
        
        # 详细报告
        with open('data/comprehensive_talent_report.txt', 'w', encoding='utf-8') as f:
            f.write("徐汇区企业人才政策综合报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总政策数量: {len(self.policies)} 条\n\n")
            
            f.write("📊 政策分类分布:\n")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                percentage = count / len(self.policies) * 100
                f.write(f"   {cat}: {count}条 ({percentage:.1f}%)\n")
            
            f.write(f"\n🏢 主要发布部门:\n")
            for dept, count in sorted(departments.items(), key=lambda x: x[1], reverse=True)[:10]:
                if count > 0 and dept != '未知':
                    f.write(f"   {dept}: {count}条\n")
            
            f.write(f"\n\n📋 详细政策列表:\n")
            f.write("-" * 80 + "\n")
            
            for i, policy in enumerate(self.policies, 1):
                f.write(f"\n{i}. {policy.get('title', '')}\n")
                f.write(f"   分类: {policy.get('category', '')}\n")
                f.write(f"   部门: {policy.get('department', '')}\n")
                f.write(f"   时间: {policy.get('publish_date', '')}\n")
                f.write(f"   链接: {policy.get('url', '')}\n")
                
                req = policy.get('company_requirements', {})
                for req_type, req_content in req.items():
                    if req_content.strip():
                        f.write(f"   【{req_type}】: {req_content[:200]}...\n")
                
                f.write("-" * 80 + "\n")
        
        print(f"\n📁 数据已导出:")
        print(f"   📋 完整数据: data/comprehensive_talent_policies.json")
        print(f"   📊 表格数据: data/comprehensive_talent_policies.csv")
        print(f"   📊 Excel文件: data/comprehensive_talent_policies.xlsx")
        print(f"   📄 详细报告: data/comprehensive_talent_report.txt")

def main():
    crawler = ComprehensiveTalentCrawler()
    crawler.crawl_policies()
    crawler.export_results()
    
    print("\n🎯 综合人才政策爬取完成！")

if __name__ == "__main__":
    main() 