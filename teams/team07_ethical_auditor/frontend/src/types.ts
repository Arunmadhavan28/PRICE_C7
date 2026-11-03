export interface AuditRecord {
  Customer_ZipCode: number | string;
  Income_Bracket: string;
  Customer_Income_Proxy: number;
  Recommended_Item_Price: number;
  Opt_in_Status: boolean;
  Item_Category: string;
  Recommendation_Algorithm: string;
  Opt_in_Clean?: boolean;
}

export interface ZipSummary {
  Customer_ZipCode?: number | string;
  "Zip Code"?: number | string;
  mean: number;
  median: number;
  std: number;
  count: number;
}

export interface BiasMetrics {
  pearson_correlation: number;
  p_value: number;
  statistically_significant: boolean;
  disparate_impact_ratio: number;
  four_fifths_violation: boolean;
  max_zip_avg_price: number;
  min_zip_avg_price: number;
  price_spread: number;
  has_steering_bias: boolean;
  zip_summary: ZipSummary[];
}

export interface PrivacyMetrics {
  total_records: number;
  breach_count: number;
  consented_count: number;
  breach_rate_pct: number;
  privacy_compliant: boolean;
  regulatory_risk: string;
}

export interface ComplianceReport {
  risk_level: string;
  risk_color: string;
  recommended_action: string;
  governance_score: number;
  privacy: PrivacyMetrics;
  bias: BiasMetrics;
}

export interface CertificateMetadata {
  certificate_id: string;
  auditor_framework: string;
  standard_alignment: string[];
  records_audited: number;
  governance_score: number;
  final_status: string;
}

export interface StreamlitArgs {
  report?: ComplianceReport;
  records?: AuditRecord[];
  breaches?: AuditRecord[];
  cert_metadata?: CertificateMetadata;
  ai_response?: {
    model: string;
    source: string;
    content: string;
  };
  scrub_executed?: boolean;
}
