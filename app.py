import streamlit as st
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import io

# 註冊 CID 中文字體（內建，不需要外部字體檔案）
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
FONT_NAME = 'STSong-Light'

# 收款資訊
BANK_NAME = "中國信託"
BANK_CODE = "822"
ACCOUNT_NUMBER = "783540208870"
ACCOUNT_NAME = "（您的戶名）"  # 可自行修改

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
        
        # 生成客戶傳送訊息
        st.subheader("📤 請複製以下訊息傳給我")
        
        if payment_option == "17,000元/月（每月付款）":
            client_message = f"""您好，我已確認廣告投放服務內容，以下是我的選擇：

【客戶名稱】{client_name}
【付款方案】17,000元/月（每月付款）
【合作啟動日期】{start_date.strftime('%Y年%m月%d日')}
【每月付款日】每月 {payment_day} 日

請確認以上資訊，謝謝！"""
        else:
            client_message = f"""您好，我已確認廣告投放服務內容，以下是我的選擇：

【客戶名稱】{client_name}
【付款方案】45,000元/三個月（一次付款）
【合作啟動日期】{start_date.strftime('%Y年%m月%d日')}
【付款日期】{payment_date.strftime('%Y年%m月%d日')}

請確認以上資訊，謝謝！"""
        
        st.code(client_message, language=None)
        st.info("💡 點擊上方文字框右上角的複製圖示，然後貼給我即可！")
        
        st.markdown("---")
        
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
                    fontSize=20,
                    alignment=1,
                    spaceAfter=30,
                    spaceBefore=10,
                    bold=True
                ),
                'heading': ParagraphStyle(
                    'Heading',
                    fontName=FONT_NAME,
                    fontSize=12,
                    spaceBefore=18,
                    spaceAfter=10,
                    bold=True
                ),
                'party': ParagraphStyle(
                    'Party',
                    fontName=FONT_NAME,
                    fontSize=11,
                    spaceBefore=5,
                    spaceAfter=5,
                    leading=18
                ),
                'normal': ParagraphStyle(
                    'Normal',
                    fontName=FONT_NAME,
                    fontSize=11,
                    spaceBefore=5,
                    spaceAfter=5,
                    leading=20,
                    firstLineIndent=22
                ),
                'normal_no_indent': ParagraphStyle(
                    'NormalNoIndent',
                    fontName=FONT_NAME,
                    fontSize=11,
                    spaceBefore=5,
                    spaceAfter=5,
                    leading=20
                ),
                'bullet': ParagraphStyle(
                    'Bullet',
                    fontName=FONT_NAME,
                    fontSize=11,
                    leftIndent=20,
                    spaceBefore=3,
                    spaceAfter=3,
                    leading=18
                ),
                'sub_bullet': ParagraphStyle(
                    'SubBullet',
                    fontName=FONT_NAME,
                    fontSize=10,
                    leftIndent=40,
                    spaceBefore=2,
                    spaceAfter=2,
                    leading=16
                ),
                'bank_info': ParagraphStyle(
                    'BankInfo',
                    fontName=FONT_NAME,
                    fontSize=11,
                    leftIndent=20,
                    spaceBefore=3,
                    spaceAfter=3,
                    leading=18
                )
            }
            
            story = []
            
            # 標題
            story.append(Paragraph("廣告投放服務合約書", styles['title']))
            
            # 計算合約期間
            if payment_option == "17,000元/月（每月付款）":
                # 月付：合約期間為一個月，可續約
                contract_end = start_date + timedelta(days=30)
                contract_period_text = f"自 {start_date.strftime('%Y 年 %m 月 %d 日')} 起至 {contract_end.strftime('%Y 年 %m 月 %d 日')} 止，共 1 個月。届期如雙方無異議，則本合約自動續行 1 個月。"
            else:
                # 季付：合約期間為三個月
                contract_end = start_date + timedelta(days=90)
                contract_period_text = f"自 {start_date.strftime('%Y 年 %m 月 %d 日')} 起至 {contract_end.strftime('%Y 年 %m 月 %d 日')} 止，共 3 個月。"
            
            # 甲方乙方
            story.append(Paragraph("<b>甲方（服務提供者）：</b>", styles['party']))
            story.append(Paragraph("<b>乙方（客戶）：</b>" + client_name, styles['party']))
            story.append(Spacer(1, 10))
            
            # 合約期間
            story.append(Paragraph("<b>合約期間</b>", styles['heading']))
            story.append(Paragraph(contract_period_text, styles['normal']))
            
            # 服務內容
            story.append(Paragraph("<b>服務內容</b>", styles['heading']))
            story.append(Paragraph("甲方同意為乙方提供以下廣告投放服務：", styles['normal']))
            story.append(Spacer(1, 5))
            
            story.append(Paragraph("<b>一、固定工作</b>", styles['normal_no_indent']))
            story.append(Paragraph("• 廣告上架", styles['bullet']))
            story.append(Paragraph("• 廣告監控／維護／優化", styles['bullet']))
            story.append(Paragraph("• 簡易週報（成果、優化計畫）", styles['bullet']))
            
            story.append(Spacer(1, 8))
            story.append(Paragraph("<b>二、非固定工作</b>", styles['normal_no_indent']))
            story.append(Paragraph("• 廣告素材建議：甲方將根據實際投放成效、競品、市場研究，提出素材建議，包含廣告文案及圖片素材上的文案供乙方調整。", styles['bullet']))
            story.append(Paragraph("• 到達頁面優化建議：甲方將監控網頁轉換成效，當轉換率出現下降狀況時，提供網頁優化建議報告予乙方。", styles['bullet']))
            
            story.append(Spacer(1, 8))
            story.append(Paragraph("<b>三、現況說明</b>", styles['normal_no_indent']))
            story.append(Paragraph(
                "目前甲方 Facebook 個人帳號暫時停用，甲方仍需每日監控乙方廣告成果。"
                "甲方將教導乙方每日匯出所需數據（甲方會預先設定好，乙方僅需每日按下匯出即可）。"
                "甲方將依每日監控狀況判斷是否需與乙方約定線上遠端控制調整後台，"
                "為避免耽誤過多時間，遠端前甲方會先做好完整調整規劃，實際操控將非常迅速。",
                styles['normal']
            ))
            
            # 費用與付款方式
            story.append(Paragraph("<b>費用與付款方式</b>", styles['heading']))
            
            if payment_option == "17,000元/月（每月付款）":
                story.append(Paragraph(
                    f"乙方同意支付甲方服務費用 <b>新台幣 17,000 元整／月</b>，於每月 {payment_day} 日前支付當月服務費用至甲方指定帳戶。",
                    styles['normal']
                ))
            else:
                story.append(Paragraph(
                    f"乙方同意支付甲方服務費用 <b>新台幣 45,000 元整（三個月）</b>，於 {payment_date.strftime('%Y 年 %m 月 %d 日')} 前一次支付至甲方指定帳戶。",
                    styles['normal']
                ))
            
            story.append(Spacer(1, 8))
            story.append(Paragraph("甲方指定帳戶：", styles['normal_no_indent']))
            story.append(Paragraph("銀行：中國信託商業銀行（822）", styles['bank_info']))
            story.append(Paragraph("帳號：783540208870", styles['bank_info']))
            
            # 發票
            story.append(Paragraph("<b>發票</b>", styles['heading']))
            story.append(Paragraph(
                "甲方應於收到乙方款項後，開立當月發票予乙方。",
                styles['normal']
            ))
            
            # 保密條款
            story.append(Paragraph("<b>保密與資料使用</b>", styles['heading']))
            story.append(Paragraph(
                "雙方承諾，合作期間所涉及之商業資訊、廣告數據及客戶資料僅用於本合作，不得對外公開或提供予第三方。如有違反，違反方願賠償他方之損失，包含但不限於訴訟費、律師費等。",
                styles['normal']
            ))
            
            # 終止條款
            story.append(Paragraph("<b>合約終止</b>", styles['heading']))
            story.append(Paragraph(
                "任一方如欲提前終止本合約，應於終止日前 14 日以書面通知他方。已支付之費用，依實際服務天數按比例計算退還。",
                styles['normal']
            ))
            
            # 爭議處理
            story.append(Paragraph("<b>爭議處理</b>", styles['heading']))
            story.append(Paragraph(
                "本合約之解釋與適用，以中華民國法律為準據法。若有爭議，雙方應本於誠信原則友好協商；倘無共識，則合意以臺灣臺北地方法院為第一審管轄法院。",
                styles['normal']
            ))
            
            story.append(Spacer(1, 40))
            
            # 簽署欄
            story.append(Paragraph("<b>簽署</b>", styles['heading']))
            story.append(Spacer(1, 15))
            
            signature_data = [
                ['甲方（服務提供者）', '', '乙方（客戶）'],
                ['', '', ''],
                ['', '', ''],
                ['簽名：___________________', '', '簽名：___________________'],
                ['', '', ''],
                ['日期：___________________', '', '日期：___________________'],
            ]
            
            signature_table = Table(signature_data, colWidths=[6.5*cm, 2*cm, 6.5*cm])
            signature_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
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
