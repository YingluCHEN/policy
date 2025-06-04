#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
徐汇区人才政策专项爬虫
专门针对企业人才引进、房屋补贴、落户服务等政策
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

class TalentFocusedCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 专门针对人才政策的URL
        self.urls = [
            # 政务公开 - 更多页面
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=2",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=3",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=4",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=5",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_xxgyhb&page=6",
            
            # 人力资源和社会保障局 - 重点扩展
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=2",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=3",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=4",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=5",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_rshbj&page=6",
            
            # 住房保障和房屋管理局 - 重点关注
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_zfbzj&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_zfbzj&page=2",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_zfbzj&page=3",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_zfbzj&page=4",
            
            # 科学技术委员会
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=2",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=3",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=4",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_kjw&page=5",
            
            # 教育局 - 人才子女教育
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_jyj&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_jyj&page=2",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_jyj&page=3",
            
            # 卫生健康委员会 - 人才医疗服务
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_wsjkw&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_wsjkw&page=2",
            
            # 公安分局 - 落户服务
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_gafj&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_gafj&page=2",
            
            # 通知公告 - 人才相关通知
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_gggs&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_gggs&page=2",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_gggs&page=3",
            
            # 规范性文件
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_zcwj&page=1",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_zcwj&page=2",
            "https://www.xuhui.gov.cn/xxgk/portal/article/organizationArticle?code=xhxxgk_wbj_zcwj&page=3",
            
            # 专门的人才政策搜索
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=人才引进",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=人才补贴",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=住房补贴",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=人才公寓",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=落户",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=人才服务",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=高层次人才",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=海外人才",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=博士",
            "https://www.xuhui.gov.cn/search/pcRender?pageId=51bc01c2a0b04b5e8816d5eaea8c6df4&advance=true&tpl=2068&keyword=硕士",
        ]
        
        # 专门的人才政策关键词
        self.talent_keywords = [
            # 人才引进类
            "人才引进", "人才招聘", "人才计划", "高层次人才", "领军人才", "拔尖人才",
            "青年人才", "海外人才", "外籍人才", "专家", "学者", "科学家",
            "博士", "硕士", "教授", "研究员", "工程师", "院士",
            "千人计划", "万人计划", "杰青", "长江学者", "博士后", "海归", "留学人员",
            
            # 住房保障类
            "住房补贴", "房屋补贴", "租房补贴", "购房补贴", "住房支持", "住房优惠",
            "人才公寓", "人才房", "保障性住房", "公租房", "廉租房", "租赁住房",
            "安居工程", "住房保障", "租金补贴", "房租补助",
            
            # 落户服务类
            "落户", "户籍", "居住证", "积分落户", "人才落户", "直接落户",
            "迁户", "户口", "居住证积分", "落户政策", "户籍政策",
            
            # 子女教育类
            "子女入学", "子女教育", "教育优惠", "入学政策", "学区", "择校",
            "教育补贴", "学费减免", "国际学校", "优质教育",
            
            # 医疗保障类
            "医疗保障", "医疗服务", "健康服务", "体检", "医疗优惠",
            "医疗补贴", "就医绿色通道", "健康管理",
            
            # 配偶就业类
            "配偶就业", "家属就业", "就业支持", "职业介绍", "就业服务",
            
            # 创业支持类
            "创业支持", "创业补贴", "创业孵化", "创业基金", "创业扶持",
            "初创企业", "创业园", "众创空间",
            
            # 资金支持类
            "人才资助", "人才奖励", "科研资助", "项目资助", "启动资金",
            "津贴", "补助", "奖金", "激励", "扶持资金",
            
            # 申报相关
            "申报", "申请", "条件", "要求", "材料", "流程", "办理",
            "审核", "评审", "认定", "资格", "标准"
        ]
        
        # 企业人才政策申报条件关键词
        self.application_keywords = {
            "企业基本条件": [
                "注册地", "注册资本", "实缴资本", "经营期限", "营业执照",
                "企业性质", "所有制", "行业类别", "经营范围", "成立时间",
                "营业收入", "纳税额", "员工规模", "技术人员比例", "研发投入",
                "高新技术企业", "专精特新", "独角兽企业", "上市公司"
            ],
            "人才条件要求": [
                "学历要求", "学位要求", "专业要求", "工作经验", "年龄限制",
                "技术职称", "专业技能", "语言能力", "海外经历", "工作业绩",
                "科研成果", "专利发明", "获奖情况", "推荐信", "学术声誉"
            ],
            "申报材料清单": [
                "申报表", "申请表", "身份证明", "学历证明", "学位证书",
                "工作证明", "推荐信", "简历", "业绩材料", "获奖证书",
                "财务报表", "纳税证明", "企业资质", "专利证书", "论文著作"
            ],
            "申报时间安排": [
                "申报时间", "截止时间", "受理期间", "评审时间", "公示时间",
                "办理时限", "有效期", "年度申报", "批次申报", "常年受理"
            ],
            "资金支持标准": [
                "补贴标准", "奖励金额", "支持额度", "最高限额", "分级支持",
                "一次性", "按年度", "分期拨付", "配套资金", "专项资金"
            ],
            "住房支持政策": [
                "住房补贴", "租金补贴", "购房优惠", "人才公寓", "免费居住",
                "租金减免", "购房资助", "住房分配", "优先购房", "租赁补贴"
            ],
            "落户服务条件": [
                "落户条件", "积分要求", "居住证", "社保缴费", "纳税记录",
                "落户流程", "办理材料", "审批时间", "配偶落户", "子女落户"
            ],
            "其他配套服务": [
                "子女入学", "医疗服务", "配偶就业", "创业支持", "培训机会",
                "学术交流", "职业发展", "绿色通道", "一站式服务", "专员服务"
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
        """从列表页提取政策链接 - 人才政策专用版"""
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # 多种选择器策略
        link_selectors = [
            'a[href*="detail"]',
            'a[href*="article"]',
            '.list-item a',
            '.title a',
            'li a',
            '.policy-title a',
            '.news-title a'
        ]
        
        found_links = []
        for selector in link_selectors:
            found_links.extend(soup.select(selector))
        
        # 人才政策识别
        seen_hrefs = set()
        for a in found_links:
            href = a.get('href')
            title = a.get_text(strip=True)
            
            if href and href not in seen_hrefs and len(title) > 5:
                # 更精确的人才政策识别
                is_talent_related = any(keyword in title for keyword in self.talent_keywords)
                
                if is_talent_related:
                    full_url = urljoin(base_url, href)
                    links.append({
                        'title': title,
                        'url': full_url
                    })
                    seen_hrefs.add(href)
        
        return links

    def extract_policy_content(self, url):
        """提取政策详细内容"""
        html = self.fetch_page(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
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
        
        # 提取内容
        content = ""
        content_selectors = [
            '.content', '.art-content', '.main-content', '.policy-content',
            '[class*="content"]', '.main', 'article', '.detail', '.text'
        ]
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                for nav in content_elem.select('nav, .nav, .menu, .breadcrumb, .pagination'):
                    nav.decompose()
                content = content_elem.get_text(strip=True)
                if len(content) > 200:
                    break
        
        if not content or len(content) < 100:
            body = soup.find('body')
            if body:
                for elem in body.select('nav, .nav, .menu, .sidebar, .footer, .header'):
                    elem.decompose()
                content = body.get_text(strip=True)
        
        # 提取发布时间
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
        
        # 提取发布部门
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
            'content': content[:6000],
            'publish_date': publish_date,
            'department': department,
            'crawl_time': datetime.now().isoformat()
        }

    def classify_policy(self, policy):
        """人才政策分类"""
        text = f"{policy['title']} {policy['content']}"
        
        categories = {
            "人才引进": [
                "人才引进", "人才招聘", "海外人才", "高层次人才", "领军人才",
                "专家", "博士", "硕士", "院士", "千人计划", "万人计划"
            ],
            "住房保障": [
                "住房补贴", "房屋补贴", "租房补贴", "人才公寓", "住房支持",
                "保障性住房", "公租房", "廉租房", "安居", "租金"
            ],
            "落户服务": [
                "落户", "户籍", "居住证", "积分", "迁户", "户口", "落户政策"
            ],
            "子女教育": [
                "子女入学", "子女教育", "教育优惠", "入学", "学区", "择校"
            ],
            "医疗保障": [
                "医疗保障", "医疗服务", "健康", "体检", "医疗优惠", "就医"
            ],
            "创业支持": [
                "创业支持", "创业补贴", "创业孵化", "创业基金", "初创", "众创"
            ],
            "资金资助": [
                "人才资助", "人才奖励", "科研资助", "项目资助", "津贴", "补助"
            ],
            "配偶就业": [
                "配偶就业", "家属就业", "就业支持", "职业介绍"
            ]
        }
        
        # 计算分类得分
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

    def extract_application_requirements(self, policy):
        """提取企业人才政策申报要求"""
        text = f"{policy['title']} {policy['content']}"
        requirements = {}
        
        for req_type, keywords in self.application_keywords.items():
            found_requirements = []
            
            for keyword in keywords:
                sentences = re.split(r'[。！？；\n]', text)
                for sentence in sentences:
                    if keyword in sentence and len(sentence.strip()) > 10:
                        cleaned = sentence.strip()
                        if (len(cleaned) > 15 and 
                            not cleaned.startswith(('首页', '返回', '上一页', '下一页')) and
                            not all(c in '=- \t' for c in cleaned)):
                            found_requirements.append(cleaned)
            
            # 去重并限制数量
            unique_requirements = []
            seen = set()
            for req in found_requirements:
                if req not in seen and len(req) < 400:
                    unique_requirements.append(req)
                    seen.add(req)
                if len(unique_requirements) >= 6:
                    break
            
            requirements[req_type] = "; ".join(unique_requirements) if unique_requirements else ""
        
        return requirements

    def crawl_talent_policies(self):
        """爬取人才政策"""
        print("开始专项爬取徐汇区企业人才政策...")
        print(f"将爬取 {len(self.urls)} 个人才政策专用URL源")
        
        os.makedirs('data', exist_ok=True)
        
        all_links = []
        
        # 并发爬取
        def fetch_links(url):
            html = self.fetch_page(url)
            if html:
                return self.extract_policy_links(html, url)
            return []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_url = {executor.submit(fetch_links, url): url for url in self.urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    links = future.result()
                    all_links.extend(links)
                    if links:
                        print(f"从 {url} 获取到 {len(links)} 个人才政策链接")
                except Exception as e:
                    print(f"处理 {url} 时出错: {e}")
                time.sleep(0.5)
        
        # 去重
        unique_links = []
        seen_urls = set()
        for link in all_links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        print(f"去重后共找到 {len(unique_links)} 个人才政策链接")
        
        # 爬取详细内容，增加到60个
        target_links = unique_links[:60]
        print(f"将详细爬取前 {len(target_links)} 个人才政策")
        
        for i, link in enumerate(target_links, 1):
            print(f"正在处理第 {i}/{len(target_links)} 个政策: {link['title'][:60]}...")
            
            policy = self.extract_policy_content(link['url'])
            if policy and len(policy['content']) > 150:
                policy['category'] = self.classify_policy(policy)
                policy['application_requirements'] = self.extract_application_requirements(policy)
                
                # 保留人才相关政策
                req = policy['application_requirements']
                has_talent_req = any(
                    len(v.strip()) > 15 for v in req.values() if v
                )
                
                talent_categories = ['人才引进', '住房保障', '落户服务', '子女教育', '医疗保障', '创业支持', '资金资助', '配偶就业']
                
                if has_talent_req or policy['category'] in talent_categories:
                    self.policies.append(policy)
                    print(f"  ✅ 已保存 (分类: {policy['category']})")
                else:
                    print(f"  ❌ 跳过 (非人才政策)")
            
            time.sleep(1.2)
        
        print(f"\n🎯 成功爬取 {len(self.policies)} 个人才政策")

    def analyze_and_export(self):
        """分析并导出人才政策数据"""
        if not self.policies:
            print("没有爬取到有效数据")
            return
        
        print("正在分析人才政策数据...")
        
        # 统计分析
        categories = {}
        departments = {}
        policies_with_requirements = 0
        
        for policy in self.policies:
            cat = policy.get('category', '其他')
            categories[cat] = categories.get(cat, 0) + 1
            
            dept = policy.get('department', '未知')
            departments[dept] = departments.get(dept, 0) + 1
            
            req = policy.get('application_requirements', {})
            if any(v.strip() for v in req.values() if v):
                policies_with_requirements += 1
        
        # 导出JSON
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
        
        # 导出CSV
        df_data = []
        for policy in self.policies:
            req = policy.get('application_requirements', {})
            df_data.append({
                '标题': policy.get('title', ''),
                '分类': policy.get('category', ''),
                '发布部门': policy.get('department', ''),
                '发布时间': policy.get('publish_date', ''),
                '链接': policy.get('url', ''),
                '企业基本条件': req.get('企业基本条件', ''),
                '人才条件要求': req.get('人才条件要求', ''),
                '申报材料清单': req.get('申报材料清单', ''),
                '申报时间安排': req.get('申报时间安排', ''),
                '资金支持标准': req.get('资金支持标准', ''),
                '住房支持政策': req.get('住房支持政策', ''),
                '落户服务条件': req.get('落户服务条件', ''),
                '其他配套服务': req.get('其他配套服务', ''),
                '内容摘要': policy.get('content', '')[:300]
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv('data/talent_policies.csv', index=False, encoding='utf-8-sig')
        df.to_excel('data/talent_policies.xlsx', index=False)
        
        # 导出详细申报要求
        with open('data/talent_application_requirements.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("徐汇区企业人才政策申报要求详细汇总\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总政策数量: {len(self.policies)} 条\n")
            f.write(f"包含申报要求: {policies_with_requirements} 条\n\n")
            
            # 按分类整理
            for category in ['人才引进', '住房保障', '落户服务', '子女教育', '医疗保障', '创业支持', '资金资助', '配偶就业']:
                category_policies = [p for p in self.policies if p.get('category') == category]
                if category_policies:
                    f.write(f"\n{'='*15} {category} ({len(category_policies)}条) {'='*15}\n\n")
                    
                    for i, policy in enumerate(category_policies, 1):
                        f.write(f"{i}. {policy.get('title', '')}\n")
                        f.write(f"   📅 发布时间: {policy.get('publish_date', '未知')}\n")
                        f.write(f"   🏛️  发布部门: {policy.get('department', '未知')}\n")
                        f.write(f"   🔗 链接: {policy.get('url', '')}\n\n")
                        
                        req = policy.get('application_requirements', {})
                        for req_type, req_content in req.items():
                            if req_content.strip():
                                f.write(f"   【{req_type}】\n")
                                items = req_content.split('; ')
                                for item in items:
                                    if item.strip():
                                        f.write(f"   • {item.strip()}\n")
                                f.write("\n")
                        
                        f.write("-" * 70 + "\n\n")
        
        # 生成分析报告
        with open('data/talent_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write("徐汇区企业人才政策分析报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总政策数量: {len(self.policies)} 条\n")
            f.write(f"包含申报要求的政策: {policies_with_requirements} 条 ({policies_with_requirements/len(self.policies)*100:.1f}%)\n\n")
            
            f.write("📊 政策分类分布:\n")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                percentage = count / len(self.policies) * 100
                f.write(f"   {cat}: {count}条 ({percentage:.1f}%)\n")
            
            f.write(f"\n🏢 主要发布部门:\n")
            for dept, count in sorted(departments.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    f.write(f"   {dept}: {count}条\n")
        
        print(f"\n📁 人才政策数据已导出:")
        print(f"   🎯 详细申报要求: data/talent_application_requirements.txt")
        print(f"   📊 分析报告: data/talent_analysis_report.txt")
        print(f"   📋 完整数据: data/talent_policies.json")
        print(f"   📊 表格数据: data/talent_policies.csv")
        print(f"   📊 Excel文件: data/talent_policies.xlsx")

def main():
    crawler = TalentFocusedCrawler()
    crawler.crawl_talent_policies()
    crawler.analyze_and_export()
    
    print("\n🎯 人才政策专项爬取完成！")
    print("📋 重点查看: data/talent_application_requirements.txt")
    print("📊 分析报告: data/talent_analysis_report.txt")

if __name__ == "__main__":
    main() 