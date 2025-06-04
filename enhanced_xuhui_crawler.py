#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版徐汇区人才政策爬虫
加大检索力度，重点提取企业申报条件
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

class EnhancedXuhuiTalentCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 大幅扩展URL覆盖范围
        self.urls = [
            # 政务公开 - 扩展到更多页面
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=2", 
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=3",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=4",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=5",
            
            # 人力资源和社会保障局 - 扩展页面
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=2",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=3",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=4",
            
            # 科学技术委员会 - 扩展页面
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=2",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=3",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=4",
            
            # 商务委员会
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_sww&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_sww&page=2",
            
            # 发展和改革委员会
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_fgw&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_fgw&page=2",
            
            # 教育局
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_jyj&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_jyj&page=2",
            
            # 财政局
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_czj&page=1",
            
            # 国有资产监督管理委员会
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_gzw&page=1",
            
            # 通知公告
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_gggs&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_gggs&page=2",
            
            # 规范性文件
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_zcwj&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_zcwj&page=2",
            
            # 各委办局主站
            "https://www.xuhui.gov.cn/renshebao/",
            "https://www.xuhui.gov.cn/kejiju/", 
            "https://www.xuhui.gov.cn/jiaoyu/",
            "https://www.xuhui.gov.cn/fangtuju/",
            
            # 专题专栏
            "https://www.xuhui.gov.cn/ztlm/",
            
            # 重点领域信息公开
            "https://www.xuhui.gov.cn/zdly/",
        ]
        
        # 扩展的人才政策关键词
        self.talent_keywords = [
            # 人才相关
            "人才", "高层次人才", "领军人才", "拔尖人才", "青年人才", "海外人才", "引进人才",
            "专家", "博士", "硕士", "教授", "研究员", "工程师", "科学家", "学者",
            "千人计划", "万人计划", "杰青", "长江学者", "院士", "博士后", "海归", "留学人员",
            
            # AI和科技相关  
            "AI", "人工智能", "智能", "算法", "机器学习", "深度学习", "大模型", "生成式AI",
            "具身智能", "大模型", "科创", "科技", "研发", "创新", "技术", "数字化",
            "新型工业化", "先导区", "科创街区", "孵化器", "加速器",
            
            # 创业支持
            "创业", "孵化", "初创", "创新创业", "双创", "创客", "众创空间", "科技园",
            "产业园", "天使投资", "风投", "融资", "投资",
            
            # 资金支持
            "补贴", "资助", "奖励", "扶持", "资金", "支持", "专项", "基金", "经费",
            "财政", "拨款", "补助", "贴息", "减免", "优惠",
            
            # 申报相关
            "申报", "申请", "条件", "要求", "材料", "截止", "期限", "评审", "审核",
            "准入", "资格", "标准", "门槛", "流程", "程序"
        ]
        
        # 大幅增强的企业申报条件关键词
        self.application_keywords = {
            "企业基本要求": [
                "注册地", "注册资本", "实缴资本", "营业收入", "年收入", "年营业额", 
                "纳税", "税收", "规模", "行业", "资质", "成立时间", "经营期限",
                "高新技术企业", "独角兽企业", "专精特新", "小巨人", "瞪羚企业",
                "从业人员", "员工数", "技术人员", "研发人员", "博士数量", "硕士数量"
            ],
            "申报条件": [
                "申报条件", "基本条件", "准入条件", "资格条件", "申请条件",
                "学历要求", "工作经验", "年龄限制", "专业背景", "技术要求",
                "业绩要求", "财务要求", "信用要求", "合规要求", "环保要求"
            ],
            "申报材料": [
                "申报材料", "申请材料", "证明材料", "附件", "申请表", "申报表",
                "推荐信", "简历", "学历证明", "工作证明", "业绩证明",
                "财务报表", "审计报告", "税务证明", "资质证书", "专利证书"
            ],
            "申报时间": [
                "截止时间", "申报时间", "申报期间", "受理时间", "办理时限",
                "有效期", "评审时间", "公示时间", "发布时间", "开始时间",
                "结束时间", "年度申报", "季度申报", "月度申报"
            ],
            "资金支持": [
                "资金支持", "补贴标准", "奖励标准", "支持额度", "最高支持",
                "按比例", "一次性", "分期", "年度支持", "配套资金",
                "专项资金", "引导基金", "风险补偿", "贴息支持"
            ],
            "其他优惠": [
                "税收优惠", "租金优惠", "用地优惠", "人才服务", "绿色通道",
                "优先推荐", "重点支持", "配套服务", "政策倾斜"
            ]
        }
        
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

    def extract_policy_links(self, html, base_url):
        """从列表页提取政策链接 - 增强版"""
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # 多种选择器策略
        link_selectors = [
            'a[href*="detail"]',  # 包含detail的链接
            'a[href*="article"]', # 包含article的链接
            '.list-item a',       # 列表项中的链接
            '.title a',           # 标题链接
            'li a',               # 列表中的链接
        ]
        
        found_links = []
        for selector in link_selectors:
            found_links.extend(soup.select(selector))
        
        # 去重并过滤
        seen_hrefs = set()
        for a in found_links:
            href = a.get('href')
            title = a.get_text(strip=True)
            
            if href and href not in seen_hrefs and len(title) > 5:
                # 更宽松的人才政策识别
                is_talent_related = (
                    any(keyword in title for keyword in self.talent_keywords) or
                    any(keyword in title.lower() for keyword in ['policy', 'support', 'fund', 'grant']) or
                    len([k for k in self.talent_keywords if k in title]) > 0
                )
                
                if is_talent_related:
                    full_url = urljoin(base_url, href)
                    links.append({
                        'title': title,
                        'url': full_url
                    })
                    seen_hrefs.add(href)
        
        return links

    def extract_policy_content(self, url):
        """提取政策详细内容 - 增强版"""
        html = self.fetch_page(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题 - 多种策略
        title = ""
        title_selectors = [
            'h1', 'h2', '.title', '.art-title', '.page-title', 
            '[class*="title"]', '[class*="head"]', '.main-title'
        ]
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and len(title_elem.get_text(strip=True)) > 5:
                title = title_elem.get_text(strip=True)
                break
        
        # 提取内容 - 多种策略
        content = ""
        content_selectors = [
            '.content', '.art-content', '.main-content', '.policy-content',
            '[class*="content"]', '.main', 'article', '.detail', '.text'
        ]
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 移除导航、菜单等无关内容
                for nav in content_elem.select('nav, .nav, .menu, .breadcrumb, .pagination'):
                    nav.decompose()
                content = content_elem.get_text(strip=True)
                if len(content) > 200:  # 确保内容足够长
                    break
        
        # 如果没找到特定的内容区域，取body内容但排除导航
        if not content or len(content) < 100:
            body = soup.find('body')
            if body:
                # 移除导航元素
                for elem in body.select('nav, .nav, .menu, .sidebar, .footer, .header'):
                    elem.decompose()
                content = body.get_text(strip=True)
        
        # 提取发布时间 - 增强模式
        publish_date = ""
        date_patterns = [
            r'(\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?)',
            r'(\d{4}/\d{1,2}/\d{1,2})',
            r'(\d{4}\.\d{1,2}\.\d{1,2})',
            r'发布时间[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2})',
            r'时间[：:]\s*(\d{4}[-年]\d{1,2}[-月]\d{1,2})'
        ]
        
        search_text = content + title + str(soup)
        for pattern in date_patterns:
            match = re.search(pattern, search_text)
            if match:
                publish_date = match.group(1)
                break
        
        # 提取发布部门 - 增强模式
        department = ""
        dept_patterns = [
            r'发布机构[：:]\s*([^，。；！？\n]+)',
            r'发布部门[：:]\s*([^，。；！？\n]+)',
            r'(徐汇区[^，。；！？\n]*?[局|委|办|中心|部|处])',
            r'(上海市徐汇区[^，。；！？\n]*?[局|委|办|中心|部|处])'
        ]
        
        for pattern in dept_patterns:
            match = re.search(pattern, search_text)
            if match:
                department = match.group(1).strip()
                break
        
        return {
            'title': title,
            'url': url,
            'content': content[:5000],  # 增加内容长度
            'publish_date': publish_date,
            'department': department,
            'crawl_time': datetime.now().isoformat()
        }

    def classify_policy(self, policy):
        """政策分类 - 增强版"""
        text = f"{policy['title']} {policy['content']}"
        
        # 更精确的分类规则
        categories = {
            "AI/人工智能": [
                "AI", "人工智能", "智能", "算法", "机器学习", "深度学习", 
                "大模型", "生成式AI", "具身智能", "大模型", "先导区"
            ],
            "人才引进": [
                "人才引进", "海外人才", "高层次人才", "领军人才", "专家引进",
                "院士", "千人计划", "万人计划", "杰青", "长江学者"
            ],
            "创业扶持": [
                "创业", "孵化", "初创", "创新创业", "双创", "创客", 
                "众创空间", "孵化器", "加速器"
            ],
            "资金补贴": [
                "补贴", "资助", "奖励", "资金支持", "专项资金", "扶持资金",
                "财政补贴", "科研经费", "启动资金"
            ],
            "产业发展": [
                "产业发展", "新型工业化", "科技园", "产业园", "科创街区",
                "低空经济", "元宇宙", "数字化"
            ],
            "住房保障": [
                "住房", "租房", "购房", "安居", "人才公寓", "住房补贴"
            ],
            "子女教育": [
                "子女", "教育", "入学", "就学", "学校", "教育优惠"
            ],
            "落户服务": [
                "落户", "户籍", "居住证", "积分", "迁户"
            ]
        }
        
        # 计算每个分类的得分
        category_scores = {}
        for category, keywords in categories.items():
            score = 0
            for keyword in keywords:
                # 标题中的关键词权重更高
                if keyword in policy['title']:
                    score += 3
                # 内容中的关键词
                if keyword in policy['content']:
                    score += 1
            category_scores[category] = score
        
        # 返回得分最高的分类
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return "其他"

    def extract_application_requirements(self, policy):
        """提取企业申报要求 - 大幅增强版"""
        text = f"{policy['title']} {policy['content']}"
        requirements = {}
        
        for req_type, keywords in self.application_keywords.items():
            found_requirements = []
            
            for keyword in keywords:
                # 使用更精确的句子分割
                sentences = re.split(r'[。！？；\n]', text)
                for sentence in sentences:
                    if keyword in sentence and len(sentence.strip()) > 10:
                        cleaned = sentence.strip()
                        # 过滤掉太短或无意义的句子
                        if (len(cleaned) > 15 and 
                            not cleaned.startswith(('首页', '返回', '上一页', '下一页')) and
                            not all(c in '=- \t' for c in cleaned)):
                            found_requirements.append(cleaned)
            
            # 去重、排序并限制数量
            unique_requirements = []
            seen = set()
            for req in found_requirements:
                if req not in seen and len(req) < 300:  # 避免过长的句子
                    unique_requirements.append(req)
                    seen.add(req)
                if len(unique_requirements) >= 5:  # 增加每类的数量
                    break
            
            requirements[req_type] = "; ".join(unique_requirements) if unique_requirements else ""
        
        return requirements

    def crawl_all_policies(self):
        """爬取所有政策 - 增强版"""
        print("开始大力度爬取徐汇区人才政策...")
        print(f"将爬取 {len(self.urls)} 个URL源")
        
        # 创建输出目录
        os.makedirs('data', exist_ok=True)
        
        all_links = []
        
        # 并发爬取链接
        def fetch_links(url):
            html = self.fetch_page(url)
            if html:
                return self.extract_policy_links(html, url)
            return []
        
        # 使用线程池加速链接收集
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_url = {executor.submit(fetch_links, url): url for url in self.urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    links = future.result()
                    all_links.extend(links)
                    print(f"从 {url} 获取到 {len(links)} 个相关链接")
                except Exception as e:
                    print(f"处理 {url} 时出错: {e}")
                time.sleep(0.5)  # 控制频率
        
        # 去重
        unique_links = []
        seen_urls = set()
        for link in all_links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        print(f"去重后共找到 {len(unique_links)} 个人才相关政策链接")
        
        # 限制爬取数量但增加到50个
        target_links = unique_links[:50]
        print(f"将详细爬取前 {len(target_links)} 个政策")
        
        # 提取每个政策的详细内容
        for i, link in enumerate(target_links, 1):
            print(f"正在处理第 {i}/{len(target_links)} 个政策: {link['title'][:60]}...")
            
            policy = self.extract_policy_content(link['url'])
            if policy and len(policy['content']) > 200:  # 提高内容质量要求
                policy['category'] = self.classify_policy(policy)
                policy['application_requirements'] = self.extract_application_requirements(policy)
                
                # 只保留有实际申报要求的政策
                req = policy['application_requirements']
                has_meaningful_req = any(
                    len(v.strip()) > 20 for v in req.values() if v
                )
                
                if has_meaningful_req or policy['category'] in ['AI/人工智能', '人才引进', '创业扶持']:
                    self.policies.append(policy)
                    print(f"  ✅ 已保存 (分类: {policy['category']})")
                else:
                    print(f"  ❌ 跳过 (无有效申报要求)")
            
            time.sleep(1.5)  # 爬取间隔
        
        print(f"\n🎯 成功爬取 {len(self.policies)} 个高质量政策")

    def analyze_and_export(self):
        """分析数据并导出 - 增强版"""
        if not self.policies:
            print("没有爬取到有效数据")
            return
        
        print("正在深度分析数据...")
        
        # 统计分析
        categories = {}
        departments = {}
        policies_with_requirements = 0
        ai_policies = 0
        
        for policy in self.policies:
            # 分类统计
            cat = policy.get('category', '其他')
            categories[cat] = categories.get(cat, 0) + 1
            
            if cat == 'AI/人工智能':
                ai_policies += 1
            
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
            'ai_policies': ai_policies,
            'statistics': {
                'categories': categories,
                'departments': departments,
                'policies_with_requirements': policies_with_requirements
            },
            'policies': self.policies
        }
        
        with open('data/enhanced_talent_policies.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # 导出详细的CSV格式
        df_data = []
        for policy in self.policies:
            req = policy.get('application_requirements', {})
            df_data.append({
                '标题': policy.get('title', ''),
                '分类': policy.get('category', ''),
                '发布部门': policy.get('department', ''),
                '发布时间': policy.get('publish_date', ''),
                '链接': policy.get('url', ''),
                '企业基本要求': req.get('企业基本要求', ''),
                '申报条件': req.get('申报条件', ''),
                '申报材料': req.get('申报材料', ''),
                '申报时间': req.get('申报时间', ''),
                '资金支持': req.get('资金支持', ''),
                '其他优惠': req.get('其他优惠', ''),
                '内容摘要': policy.get('content', '')[:300]
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv('data/enhanced_talent_policies.csv', index=False, encoding='utf-8-sig')
        df.to_excel('data/enhanced_talent_policies.xlsx', index=False)
        
        # 导出企业申报要求详细汇总
        with open('data/detailed_application_requirements.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("徐汇区人才政策企业申报要求详细汇总 (增强版)\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总政策数量: {len(self.policies)} 条\n")
            f.write(f"AI相关政策: {ai_policies} 条\n")
            f.write(f"包含申报要求: {policies_with_requirements} 条\n\n")
            
            # 按分类整理
            for category in ['AI/人工智能', '人才引进', '创业扶持', '资金补贴', '产业发展']:
                category_policies = [p for p in self.policies if p.get('category') == category]
                if category_policies:
                    f.write(f"\n{'='*20} {category} ({len(category_policies)}条) {'='*20}\n\n")
                    
                    for i, policy in enumerate(category_policies, 1):
                        f.write(f"{i}. {policy.get('title', '')}\n")
                        f.write(f"   📅 发布时间: {policy.get('publish_date', '未知')}\n")
                        f.write(f"   🏛️  发布部门: {policy.get('department', '未知')}\n")
                        f.write(f"   🔗 链接: {policy.get('url', '')}\n\n")
                        
                        req = policy.get('application_requirements', {})
                        for req_type, req_content in req.items():
                            if req_content.strip():
                                f.write(f"   【{req_type}】\n")
                                # 分行显示，提高可读性
                                items = req_content.split('; ')
                                for item in items:
                                    if item.strip():
                                        f.write(f"   • {item.strip()}\n")
                                f.write("\n")
                        
                        f.write("-" * 80 + "\n\n")
        
        # 生成增强分析报告
        with open('data/enhanced_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write("徐汇区人才政策深度分析报告 (增强版)\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总政策数量: {len(self.policies)} 条\n")
            f.write(f"AI相关政策: {ai_policies} 条 ({ai_policies/len(self.policies)*100:.1f}%)\n")
            f.write(f"包含申报要求的政策: {policies_with_requirements} 条 ({policies_with_requirements/len(self.policies)*100:.1f}%)\n\n")
            
            f.write("📊 政策分类分布:\n")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                percentage = count / len(self.policies) * 100
                f.write(f"   {cat}: {count}条 ({percentage:.1f}%)\n")
            
            f.write(f"\n🏢 主要发布部门:\n")
            for dept, count in sorted(departments.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    f.write(f"   {dept}: {count}条\n")
            
            # AI政策特别分析
            f.write(f"\n🤖 AI政策特别分析:\n")
            ai_policy_list = [p for p in self.policies if p.get('category') == 'AI/人工智能']
            for policy in ai_policy_list:
                f.write(f"   • {policy.get('title', '')}\n")
        
        print(f"\n📁 增强版数据已导出到 data/ 目录:")
        print(f"   🎯 详细申报要求: data/detailed_application_requirements.txt")
        print(f"   📊 深度分析报告: data/enhanced_analysis_report.txt")
        print(f"   📋 完整数据: data/enhanced_talent_policies.json")
        print(f"   📊 表格数据: data/enhanced_talent_policies.csv")
        print(f"   📊 Excel文件: data/enhanced_talent_policies.xlsx")

def main():
    crawler = EnhancedXuhuiTalentCrawler()
    crawler.crawl_all_policies()
    crawler.analyze_and_export()
    
    print("\n🎯 增强版爬取完成！重点查看:")
    print("📋 详细企业申报要求: data/detailed_application_requirements.txt")
    print("📊 深度分析报告: data/enhanced_analysis_report.txt")

if __name__ == "__main__":
    main() 