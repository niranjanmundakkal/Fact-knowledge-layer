"""
Script to generate the starter PDF documents for Delhivery & Economic Survey Case Studies:
1. Delhivery_IPO_Prospectus_2022.pdf
2. Delhivery_Q4_FY24_Earnings_Presentation.pdf
3. Delhivery_Annual_Report_2023_24.pdf
4. India_Economic_Survey_2024_25.pdf
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def create_prospectus_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "Delhivery_IPO_Prospectus_2022.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#b91c1c"),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # PAGE 1: Overview & Offer Details
    story.append(Paragraph("DELHIVERY LIMITED", title_style))
    story.append(Paragraph("PROSPECTUS DATED MAY 14, 2022", subtitle_style))
    story.append(Paragraph("Corporate Identity Number: U63090DL2011PLC221234", subtitle_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Registered Office:</b> N24-N34, S24-S34, Air Cargo Logistics Centre-II, Opposite Gate 6 Cargo Terminal, Indira Gandhi International Airport, New Delhi 110037, India.", body_style))
    story.append(Paragraph("<b>Corporate Office:</b> Plot 5, Sector 44, Gurugram 122002, Haryana, India.", body_style))
    story.append(Paragraph("<b>Contact Person:</b> Sunil Kumar Bansal, Company Secretary and Compliance Officer.", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("DETAILS OF THE INITIAL PUBLIC OFFER (IPO)", h2_style))
    offer_data = [
        ["Type of Issue", "Number of Equity Shares", "Total Issue Size (₹ in million)"],
        ["Fresh Issue", "82,152,503 Equity Shares", "₹40,000.00 million"],
        ["Offer for Sale (OFS)", "25,364,585 Equity Shares", "₹12,350.00 million"],
        ["Total Offer Size", "107,517,088 Equity Shares", "₹52,350.00 million"]
    ]
    t = Table(offer_data, colWidths=[160, 180, 180])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("SUMMARY OF THE BUSINESS AND NETWORK INFRASTRUCTURE", h2_style))
    story.append(Paragraph(
        "According to the RedSeer Report, Delhivery Limited was the largest and fastest growing fully-integrated logistics services player in India by revenue as of Fiscal 2021. "
        "As of December 31, 2021, the Company provided logistics services across 17,488 postal index number ('PIN') codes in India, covering 90.61% of all Indian PIN codes. "
        "The Company's infrastructure network includes 122 gateways, 21 automated sort centres, 93 fulfilment centres, and 2,521 direct delivery centres. "
        "Total active team size reached 86,184 personnel as of December 31, 2021, including permanent and contractual employees.", body_style
    ))
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # PAGE 2: Financial Information & Management
    story.append(Paragraph("HISTORICAL RESTATED FINANCIAL INFORMATION", h2_style))
    story.append(Paragraph(
        "The following details are derived from the Restated Consolidated Financial Statements of Delhivery Limited for Fiscal 2019, Fiscal 2020, and Fiscal 2021 (in ₹ million):", body_style
    ))
    story.append(Spacer(1, 8))

    fin_data = [
        ["Financial Metric", "Fiscal 2019", "Fiscal 2020", "Fiscal 2021", "9M ended Dec 31, 2021"],
        ["Revenue from Contracts", "₹16,538.97M", "₹27,805.75M", "₹36,465.27M", "₹48,105.30M"],
        ["Total Income", "₹16,948.74M", "₹29,886.29M", "₹38,382.91M", "₹49,114.06M"],
        ["Restated Loss for Year", "₹(17,833.04)M", "₹(2,689.26)M", "₹(4,157.43)M", "₹(8,911.39)M"],
        ["Adjusted EBITDA", "₹(1,876.44)M", "₹(2,531.93)M", "₹(2,532.83)M", "₹(348.01)M"],
        ["Total Assets", "₹40,625.45M", "₹43,573.08M", "₹45,977.98M", "₹84,294.83M"]
    ]
    t2 = Table(fin_data, colWidths=[140, 95, 95, 95, 100])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    story.append(Paragraph("BOARD OF DIRECTORS AND KEY MANAGERIAL PERSONNEL", h2_style))
    story.append(Paragraph(
        "As on the date of this Prospectus, the Board of Directors includes:<br/>"
        "• <b>Deepak Kapoor</b>: Chairman and Non-Executive Independent Director (DIN: 00162957).<br/>"
        "• <b>Sahil Barua</b>: Managing Director and Chief Executive Officer (DIN: 05131571), associated since incorporation on December 19, 2011.<br/>"
        "• <b>Sandeep Kumar Barasia</b>: Executive Director and Chief Business Officer (DIN: 01432123).<br/>"
        "• <b>Kapil Bharati</b>: Executive Director and Chief Technology Officer (DIN: 02227607).<br/>"
        "• <b>Suvir Suren Sujan</b>: Non-Executive Nominee Director (DIN: 01173669), nominee of Nexus Ventures.<br/>"
        "• <b>Donald Francis Colleran</b>: Non-Executive Nominee Director (DIN: 09431299), nominee of FedEx.<br/>"
        "• <b>Strategic Acquisition:</b> In August 2021, Delhivery completed the acquisition of 100% shareholding in Spoton Logistics Private Limited for integrated freight scale.", body_style
    ))

    doc.build(story)
    print(f"Generated: {pdf_path}")

def create_earnings_presentation_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "Delhivery_Q4_FY24_Earnings_Presentation.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#dc2626"),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # PAGE 1: Earnings Highlights
    story.append(Paragraph("DELHIVERY LIMITED", title_style))
    story.append(Paragraph("EARNINGS PRESENTATION - Q4 & FY24 (May 17, 2024)", subtitle_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Notice & Filing:</b> Madhulika Rawat, Company Secretary & Compliance Officer (Membership No: F8765), Place: Goa.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("EXECUTIVE HIGHLIGHTS: FY24 PERFORMANCE", h2_style))
    story.append(Paragraph(
        "• <b>FY24 Revenue from Services:</b> ₹8,142 Cr (representing YoY growth of 12.7%).<br/>"
        "• <b>Full Year EBITDA:</b> Achieved positive EBITDA of ₹127 Cr (margin 1.6%) compared to ₹(452) Cr (margin -6.3%) in FY23.<br/>"
        "• <b>Adjusted EBITDA:</b> ₹76 Cr (margin 0.9%) compared to ₹(404) Cr in FY23.<br/>"
        "• <b>Express Parcel Shipments:</b> 740 Mn shipments delivered in FY24 (YoY growth: 11.5%). Inception volume exceeded 2.8 Bn+ parcels.<br/>"
        "• <b>Part Truckload (PTL) Freight:</b> 1.4 Mn Tons PTL freight delivered in FY24 (YoY growth: 29.8%). Total PTL freight delivered since inception exceeded 4.8 Mn+ Tons.<br/>"
        "• <b>Net Working Capital (NWC):</b> Sharp reduction in NWC days from 38 days to 31 days as of March 31, 2024.<br/>"
        "• <b>Cash Position:</b> Total cash balance stood strong at ₹5,444 Cr as of March 31, 2024.", body_style
    ))
    story.append(Spacer(1, 15))

    story.append(PageBreak())

    # PAGE 2: Key Operating Metrics & Quarterly Bridge
    story.append(Paragraph("KEY OPERATING METRICS SUMMARY (AS OF Q4 FY24)", h2_style))
    
    metrics_data = [
        ["Operating Metric", "Q4 FY22", "Q4 FY23", "Q4 FY24", "YoY Trend"],
        ["Pin-code Reach", "18,074", "18,540", "18,793", "+253 codes"],
        ["Active Customers", "23,613", "27,253", "33,278", "+22.1% YoY"],
        ["Logistics Infrastructure", "18.15 Mn sq ft", "17.99 Mn sq ft", "18.82 Mn sq ft", "Expanded"],
        ["Automated Sort Centers", "21", "24", "29", "+5 centers"],
        ["Gateways", "123", "94", "111", "+17 gateways"],
        ["Reported Team Size (Footnote 4)", "60,373", "57,307", "63,713", "+11.2% YoY"],
        ["Daily Average Fleet Size", "9,120", "11,105", "15,065", "+35.7% YoY"]
    ]
    t = Table(metrics_data, colWidths=[150, 85, 85, 85, 95])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))
    story.append(Paragraph("<i>Note (4): Team size includes permanent employees and contractual workers (excluding partner agents, daily wage manpower, security guards, and last-mile delivery partner agents) as of the last day of the period.</i>", ParagraphStyle('Footnote', parent=body_style, fontSize=7.5, textColor=colors.HexColor("#64748b"))))
    story.append(Spacer(1, 15))

    story.append(Paragraph("ADJUSTED EBITDA RECONCILIATION BRIDGE (FY24 in ₹ Cr)", h2_style))
    bridge_data = [
        ["Metric", "FY23 (₹ Cr)", "FY24 (₹ Cr)", "Accounting Notes / Explanation"],
        ["Revenue from Customers", "7,225", "8,142", "Includes revenue from logistics services"],
        ["Reported EBITDA", "(452)", "127", "Full year operating EBITDA turnaround"],
        ["Add: Share based payments", "289", "226", "Non-cash accounting expense towards ESOPs"],
        ["Less: Actual lease rent paid", "258", "277", "Cash rent paid on leased properties under Ind AS 116"],
        ["Adjusted EBITDA", "(404)", "76", "Standardized operating profitability metric"]
    ]
    t2 = Table(bridge_data, colWidths=[130, 75, 75, 220])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t2)

    doc.build(story)
    print(f"Generated: {pdf_path}")

def create_annual_report_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "Delhivery_Annual_Report_2023_24.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0284c7"),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # PAGE 1: Corporate Overview & Financial Performance
    story.append(Paragraph("DELHIVERY LIMITED", title_style))
    story.append(Paragraph("ANNUAL REPORT 2023-24 (13th Annual Report - Dated July 05, 2024)", subtitle_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("DELHIVERY IN NUMBERS (AS OF MARCH 31, 2024)", h2_style))
    story.append(Paragraph(
        "• <b>Express Parcel Shipments:</b> >2.8Bn delivered since inception (740Mn shipped in FY24).<br/>"
        "• <b>Part-truckload Freight:</b> >4.8Mn tonnes delivered since inception (1,429K tonnes delivered in FY24).<br/>"
        "• <b>Pin Codes Covered:</b> 18,793 pin codes across 36 States and Union Territories.<br/>"
        "• <b>Logistics Area:</b> 18.8Mn Sq ft under management across 111 gateways and 129 freight service centers.<br/>"
        "• <b>Active Customers:</b> >33,200 active enterprise and SME customers.<br/>"
        "• <b>Total Workforce Strength:</b> 98,135 workforce strength (including permanent employees, contractual workers, and last-mile delivery partner agents). Permanent employees on the rolls stood at 23,381.", body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("CONSOLIDATED FINANCIAL PERFORMANCE (DIRECTORS' REPORT - PAGE 22 & 42)", h2_style))
    story.append(Paragraph(
        "The Standalone and Consolidated Financial Statements for FY24 are prepared in compliance with the Companies Act, 2013 and Indian Accounting Standards (Ind AS):<br/>"
        "• <b>Consolidated Revenue from Operations:</b> ₹81,415.38 million in FY24 (reported in highlights as ₹81,415Mn) as against ₹72,253.01 million for FY23, registering a growth of 12.68%.<br/>"
        "• <b>Loss for the Year:</b> ₹2,491.86 million for FY24 as against ₹10,077.79 million for FY23, a reduction of loss by 75.27%.<br/>"
        "• <b>Consolidated EBITDA:</b> ₹1,266.41 million in FY24 (1.56% margin) compared to loss of ₹4,516.08 million in FY23.<br/>"
        "• <b>Adjusted EBITDA:</b> ₹757.86 million in FY24 (0.93% margin) compared to ₹(4,038.66) million in FY23.<br/>"
        "• <b>Net Working Capital Days:</b> Reduced by 11 days from 38 days to 31 days as of March 2024, with receivable days improving to 66 days.", body_style
    ))
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # PAGE 2: Governance, People & Corporate Changes
    story.append(Paragraph("BOARD OF DIRECTORS AND KEY GOVERNANCE UPDATES", h2_style))
    story.append(Paragraph(
        "As on March 31, 2024, the Board consisted of 9 members (6 Non-Executive Independent Directors and 3 Executive Directors):<br/>"
        "• <b>Deepak Kapoor:</b> Chairperson and Non-Executive Independent Director.<br/>"
        "• <b>Sahil Barua:</b> Managing Director and Chief Executive Officer.<br/>"
        "• <b>Kapil Bharati:</b> Executive Director and Chief Technology Officer.<br/>"
        "• <b>Sandeep Kumar Barasia:</b> Executive Director and Chief Business Officer (resigned post FY24 with effect from July 01, 2024 due to personal reasons).<br/>"
        "• <b>Mr. Suvir Suren Sujan:</b> Non-Executive Nominee Director, resigned from the Board with effect from August 24, 2023 on account of preoccupation and other commitments.<br/>"
        "• <b>Mr. Donald Francis Colleran:</b> Non-Executive Nominee Director, ceased to be a Director at the conclusion of the 12th AGM on September 27, 2023.<br/>"
        "• <b>Company Secretarial Appointments:</b> Sunil Kumar Bansal resigned effective May 31, 2023; Vivek Kumar served as Company Secretary until resignation on March 27, 2024; Ms. Madhulika Rawat was appointed as Company Secretary and Compliance Officer effective May 17, 2024.", body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("HUMAN RESOURCES & DIVERSITY METRICS (BRSR & DIRECTORS' REPORT)", h2_style))
    story.append(Paragraph(
        "• <b>Female Workforce:</b> In FY24, Delhivery increased the overall headcount of female employees to 5,594 across functions and positions. This represents an increase of 59% over FY23 (when this number stood at 3,519), against an overall headcount growth of 11%.<br/>"
        "• <i>Discrepancy Note:</i> On page 8 of the Annual Report, the narrative text mentions: 'The number of female workers in our combined on-roll and off-roll workforce increased 60% year-on-year', while the adjacent infographic bullet points states 'Number of female workers increased by 59% year-on-year'.<br/>"
        "• <b>All-Women Hub:</b> In March 2024, the Company opened its first all-women-operated hub in Moga, Punjab, handling all operations including BOPTs, loading, unloading, and dispatch.<br/>"
        "• <b>Associate Companies:</b> Delhivery increased its holding in Falcon Autotech Private Limited to 39.34% (fully diluted basis) by investing ₹500.40 million during FY24.", body_style
    ))

    doc.build(story)
    print(f"Generated: {pdf_path}")

def create_economic_survey_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "India_Economic_Survey_2024_25.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#047857"),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    story.append(Paragraph("GOVERNMENT OF INDIA - ECONOMIC SURVEY 2024-25", title_style))
    story.append(Paragraph("MACROECONOMIC REVIEW & LOGISTICS SECTOR DEVELOPMENTS", subtitle_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("NATIONAL LOGISTICS & COMMERCE LANDSCAPE", h2_style))
    story.append(Paragraph(
        "According to the Economic Survey and Ministry of Commerce and Industry:<br/>"
        "• <b>Logistics Sector Size:</b> The Indian logistics sector had a market size of US$382 billion in 2021, and is projected to expand to US$531 billion by 2026, growing at a CAGR of 6% to 7% annually.<br/>"
        "• <b>Road Transportation Dominance:</b> Road freight accounts for approximately 66% of total cargo movement in India, followed by railways. Organised logistics penetration is expected to rise from 3.5% in FY20 to 15% by FY26.<br/>"
        "• <b>E-Commerce Delivery Expansion:</b> Express parcel delivery is expanding at a CAGR of 28% to 31% by value, driven by D2C commerce, social commerce, and rapid consumer formalisation.", body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("MACROECONOMIC GROWTH AND INFLATION OVERVIEW", h2_style))
    story.append(Paragraph(
        "• <b>Real GDP Growth:</b> India's real GDP grew by 6.5 per cent in FY25, positioning India as the fastest-growing major economy globally.<br/>"
        "• <b>Retail Inflation (CPI):</b> Headline CPI inflation moderated to an average of 4.6 per cent in FY25 from 5.4 per cent in FY24, supported by softening core inflation and administrative supply management.<br/>"
        "• <b>Foreign Exchange Reserves:</b> Stood at USD 640.3 billion at end-December 2024, providing import cover for over 10 months and covering approximately 90% of total external debt.", body_style
    ))

    doc.build(story)
    print(f"Generated: {pdf_path}")

if __name__ == "__main__":
    create_prospectus_pdf()
    create_earnings_presentation_pdf()
    create_annual_report_pdf()
    create_economic_survey_pdf()
