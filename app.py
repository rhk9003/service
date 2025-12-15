import streamlit as st
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

# 嘗試註冊中文字體
def register_chinese_font():
    """註冊中文字體，嘗試多個可能的字體路徑"""
    font_paths = [
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/arphic/uming.ttc',
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Chinese', font_path))
                return 'Chinese'
            except:
                continue
    
    # 如果找不到中文字體，使用預設字體
    return 'Helvetica'

FONT_NAME = register_chinese_font()

# 頁面設定
st.set_page_config(
    page_title="廣告投放服務選擇",
    page_icon="📋",
    layout="centered"
)

st.title("📋 廣告投放服務內容")
st.markdown("---")

# 服務內容說明
st.header("服務內容說明")

st.subheader("✅ 固定工作")
st.markdown("""
- **廣告上架**
- **廣告監控/維護/優化**
- **簡易週報**（成果、優化計畫）
""")

st.subheader("📌 非固定工作")
st.markdown("""
- **廣告素材建議**
  - 根據實際投放成效、競品、市場研究，提出素材建議
  - 提供廣告文案、圖片素材上的文案給您做調整

- **到達頁面優化建議**
  - 監控網頁轉換成效
  - 當轉換率出現下降狀況，提供網頁優化建議報告
""")

st.warning("""
**現況提醒：** 目前我的 FB 個人帳號仍然被停用，但我仍需要每天監控您的廣告成果。
因此我會教您怎麼每天匯出我需要的數據（我會幫您設定好，只要每天幫我按下匯出就可以了）。
我會依照每天監控狀況判斷是否要跟您約線上遠端控制調整後台。
為避免耽誤太多時間，遠端前我都會先做好完整調整規劃，實際操控都會非常快。
""")

st.markdown("---")

# 收費方式選擇
st.header("💰 收費方式選擇")

payment_option = st.radio(
    "請選擇您偏好的付款方式：",
    options=[
        "17,000元/月（每月付款）",
        "45,000元/三個月（一次付款）"
    ],
    index=0
)

st.markdown("---")

# 日期設定
st.header("📅 合作時間設定")

# 合作啟動時間
default_start = datetime.now().date() + timedelta(days=7)
start_date = st.date_input(
    "合作啟動日期",
    value=default_start,
    min_value=datetime.now().date()
)

if payment_option == "17,000元/月（每月付款）":
    st.subheader("每月付款設定")
    payment_day = st.slider(
        "每月付款日（例如：每月5號）",
        min_value=1,
        max_value=28,
        value=5,
        help="選擇每個月的付款日期"
    )
    payment_info = f"每月 {payment_day} 日付款"
    total_amount = "17,000元/月"
    contract_type = "月付方案"
else:
    st.subheader("一次付款設定")
    default_payment = start_date - timedelta(days=3)
    if default_payment < datetime.now().date():
        default_payment = datetime.now().date()
    
    payment_date = st.date_input(
        "付款日期（建議於合作啟動前完成付款）",
        value=default_payment,
        min_value=datetime.now().date(),
        max_value=start_date
    )
    payment_info = f"付款日期：{payment_date.strftime('%Y年%m月%d日')}"
    total_amount = "45,000元（三個月）"
    contract_type = "季付方案"

# 客戶資訊
st.markdown("---")
st.header("📝 客戶資訊")
client_name = st.text_input("客戶名稱/公司名稱", placeholder="請輸入您的名稱或公司名稱")

st.markdown("---")

# 生成結果
if st.button("📄 生成合約內容", type="primary", use_container_width=True):
    if not client_name:
        st.error("請輸入客戶名稱/公司名稱")
    else:
        st.success("✅ 已生成合約內容！")
        
        # 生成文字摘要
        summary = f"""
═══════════════════════════════════════
廣告投放服務合約摘要
═══════════════════════════════════════

【客戶資訊】
客戶名稱：{client_name}

【服務內容】
一、固定工作
  • 廣告上架
  • 廣告監控/維護/優化
  • 簡易週報（成果、優化計畫）

二、非固定工作
  • 廣告素材建議
    - 根據實際投放成效、競品、市場研究，提出素材建議
    - 提供廣告文案、圖片素材上的文案供調整
  • 到達頁面優化建議
    - 監控網頁轉換成效
    - 轉換率下降時提供網頁優化建議報告

【現況說明】
目前服務提供者 FB 個人帳號暫時停用，將教導客戶每日匯出所需數據，
並依監控狀況安排線上遠端控制調整後台。

【付款方案】
方案類型：{contract_type}
費用金額：{total_amount}
{payment_info}

【合作時間】
合作啟動日期：{start_date.strftime('%Y年%m月%d日')}
"""
        
        if payment_option == "17,000元/月（每月付款）":
            end_date = start_date + timedelta(days=30)
            summary += f"首期服務期間：{start_date.strftime('%Y年%m月%d日')} 至 {end_date.strftime('%Y年%m月%d日')}\n"
        else:
            end_date = start_date + timedelta(days=90)
            summary += f"服務期間：{start_date.strftime('%Y年%m月%d日')} 至 {end_date.strftime('%Y年%m月%d日')}（共三個月）\n"
        
        summary += """
═══════════════════════════════════════
"""
        
        st.subheader("📋 合約摘要（可複製）")
        st.code(summary, language=None)
        
        # 複製按鈕提示
        st.info("💡 點擊上方文字框右上角的複製圖示即可複製內容")
        
        # 生成 PDF
        st.subheader("📥 下載合約 PDF")
        
        def generate_pdf():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # 定義樣式
            styles = {
                'title': ParagraphStyle(
                    'Title',
                    fontName=FONT_NAME,
                    fontSize=18,
                    alignment=1,
                    spaceAfter=20,
                    spaceBefore=10
                ),
                'heading': ParagraphStyle(
                    'Heading',
                    fontName=FONT_NAME,
                    fontSize=14,
                    spaceBefore=15,
                    spaceAfter=10,
                    textColor=colors.HexColor('#1a5276')
                ),
                'normal': ParagraphStyle(
                    'Normal',
                    fontName=FONT_NAME,
                    fontSize=11,
                    spaceBefore=5,
                    spaceAfter=5,
                    leading=18
                ),
                'bullet': ParagraphStyle(
                    'Bullet',
                    fontName=FONT_NAME,
                    fontSize=11,
                    leftIndent=20,
                    spaceBefore=3,
                    spaceAfter=3,
                    leading=16
                ),
                'sub_bullet': ParagraphStyle(
                    'SubBullet',
                    fontName=FONT_NAME,
                    fontSize=10,
                    leftIndent=40,
                    spaceBefore=2,
                    spaceAfter=2,
                    leading=14
                ),
                'note': ParagraphStyle(
                    'Note',
                    fontName=FONT_NAME,
                    fontSize=10,
                    spaceBefore=10,
                    spaceAfter=10,
                    textColor=colors.HexColor('#666666'),
                    leading=14
                )
            }
            
            story = []
            
            # 標題
            story.append(Paragraph("廣告投放服務合約", styles['title']))
            story.append(Spacer(1, 20))
            
            # 客戶資訊
            story.append(Paragraph("【客戶資訊】", styles['heading']))
            story.append(Paragraph(f"客戶名稱：{client_name}", styles['normal']))
            story.append(Paragraph(f"合約日期：{datetime.now().strftime('%Y年%m月%d日')}", styles['normal']))
            story.append(Spacer(1, 10))
            
            # 服務內容
            story.append(Paragraph("【服務內容】", styles['heading']))
            
            story.append(Paragraph("一、固定工作", styles['normal']))
            story.append(Paragraph("• 廣告上架", styles['bullet']))
            story.append(Paragraph("• 廣告監控/維護/優化", styles['bullet']))
            story.append(Paragraph("• 簡易週報（成果、優化計畫）", styles['bullet']))
            
            story.append(Spacer(1, 5))
            story.append(Paragraph("二、非固定工作", styles['normal']))
            story.append(Paragraph("• 廣告素材建議", styles['bullet']))
            story.append(Paragraph("- 根據實際投放成效、競品、市場研究，提出素材建議", styles['sub_bullet']))
            story.append(Paragraph("- 提供廣告文案、圖片素材上的文案供調整", styles['sub_bullet']))
            story.append(Paragraph("• 到達頁面優化建議", styles['bullet']))
            story.append(Paragraph("- 監控網頁轉換成效", styles['sub_bullet']))
            story.append(Paragraph("- 轉換率下降時提供網頁優化建議報告", styles['sub_bullet']))
            
            story.append(Spacer(1, 10))
            
            # 現況說明
            story.append(Paragraph("【現況說明】", styles['heading']))
            story.append(Paragraph(
                "目前服務提供者 FB 個人帳號暫時停用，將教導客戶每日匯出所需數據"
                "（已預先設定好，只需每日按下匯出即可）。服務提供者將依監控狀況"
                "判斷是否需安排線上遠端控制調整後台，遠端前會先做好完整調整規劃，"
                "實際操控將非常迅速。",
                styles['note']
            ))
            
            # 付款資訊
            story.append(Paragraph("【付款方案】", styles['heading']))
            story.append(Paragraph(f"方案類型：{contract_type}", styles['normal']))
            story.append(Paragraph(f"費用金額：{total_amount}", styles['normal']))
            story.append(Paragraph(f"{payment_info}", styles['normal']))
            
            # 合作時間
            story.append(Paragraph("【合作時間】", styles['heading']))
            story.append(Paragraph(f"合作啟動日期：{start_date.strftime('%Y年%m月%d日')}", styles['normal']))
            
            if payment_option == "17,000元/月（每月付款）":
                end_date = start_date + timedelta(days=30)
                story.append(Paragraph(
                    f"首期服務期間：{start_date.strftime('%Y年%m月%d日')} 至 {end_date.strftime('%Y年%m月%d日')}",
                    styles['normal']
                ))
            else:
                end_date = start_date + timedelta(days=90)
                story.append(Paragraph(
                    f"服務期間：{start_date.strftime('%Y年%m月%d日')} 至 {end_date.strftime('%Y年%m月%d日')}（共三個月）",
                    styles['normal']
                ))
            
            story.append(Spacer(1, 30))
            
            # 簽名欄
            story.append(Paragraph("【雙方簽章】", styles['heading']))
            story.append(Spacer(1, 20))
            
            signature_data = [
                ['服務提供者', '', '客戶'],
                ['', '', ''],
                ['簽名：_______________', '', '簽名：_______________'],
                ['日期：_______________', '', '日期：_______________'],
            ]
            
            signature_table = Table(signature_data, colWidths=[6*cm, 3*cm, 6*cm])
            signature_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(signature_table)
            
            doc.build(story)
            buffer.seek(0)
            return buffer
        
        pdf_buffer = generate_pdf()
        
        st.download_button(
            label="⬇️ 下載合約 PDF",
            data=pdf_buffer,
            file_name=f"廣告投放服務合約_{client_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# 頁尾
st.markdown("---")
st.caption("如有任何問題，請隨時與我聯繫。")
