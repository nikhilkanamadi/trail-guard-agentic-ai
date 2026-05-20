// ===== TYPES =====
export interface Study {
  id: string;
  sponsor: string;
  protocolNumber: string;
  title: string;
  phase: string;
  therapeuticArea: string;
  indication: string;
  status: 'Active' | 'Completed' | 'On Hold' | 'Archived';
  documents: number;
  complianceScore: number;
  sites: number;
  enrolledPatients: number;
  startDate: string;
  estimatedEndDate: string;
  principalInvestigator: string;
}

export interface Document {
  id: string;
  name: string;
  studyId: string;
  type: string;
  version: string;
  status: 'Validated' | 'Pending' | 'In Review' | 'Failed';
  uploadedBy: string;
  uploadedAt: string;
  size: string;
  language: string;
  site: string;
  findings: number;
}

export interface Finding {
  id: string;
  documentId: string;
  documentName: string;
  studyId: string;
  title: string;
  description: string;
  severity: 'critical' | 'major' | 'minor' | 'info';
  category: string;
  agentSource: string;
  confidenceScore: number;
  regulatoryReference: string;
  suggestedRemediation: string;
  status: 'Open' | 'Resolved' | 'Escalated' | 'False Positive';
  createdAt: string;
}

export interface ValidationRun {
  id: string;
  documentName: string;
  studyId: string;
  status: 'Completed' | 'Running' | 'Pending' | 'Failed';
  agentsCompleted: number;
  totalAgents: number;
  startedAt: string;
  duration: string;
  findingsCount: number;
}

export interface AuditEntry {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  entity: string;
  entityType: string;
  details: string;
  ipAddress: string;
}

export interface AgentStatus {
  id: string;
  name: string;
  description: string;
  status: 'running' | 'idle' | 'error' | 'completed';
  uptime: string;
  tasksCompleted: number;
  avgProcessingTime: string;
  errorRate: number;
  lastActive: string;
  circuitBreaker: 'closed' | 'open' | 'half-open';
  queueDepth: number;
  sparklineData: number[];
}

export interface TMFZone {
  id: string;
  name: string;
  zoneNumber: number;
  completeness: number;
  totalArtifacts: number;
  completedArtifacts: number;
  sections: TMFSection[];
}

export interface TMFSection {
  id: string;
  name: string;
  artifacts: TMFArtifact[];
}

export interface TMFArtifact {
  id: string;
  name: string;
  present: boolean;
  validated: boolean;
  lastUpdated?: string;
}

// ===== MOCK DATA =====

export const studies: Study[] = [
  {
    id: 'TG-2026-0847',
    sponsor: 'Pfizer Inc.',
    protocolNumber: 'PF-07321332-0847',
    title: 'A Phase III, Randomized, Double-Blind Study of Paxlovid in High-Risk Oncology Patients',
    phase: 'Phase III',
    therapeuticArea: 'Oncology',
    indication: 'Non-Small Cell Lung Cancer',
    status: 'Active',
    documents: 342,
    complianceScore: 94.2,
    sites: 48,
    enrolledPatients: 1250,
    startDate: '2025-03-15',
    estimatedEndDate: '2027-09-30',
    principalInvestigator: 'Dr. Sarah Chen',
  },
  {
    id: 'TG-2026-0623',
    sponsor: 'Novartis AG',
    protocolNumber: 'NVS-LCZ696-0623',
    title: 'Entresto Efficacy in Pediatric Heart Failure: A Multicenter Controlled Trial',
    phase: 'Phase II',
    therapeuticArea: 'Cardiology',
    indication: 'Pediatric Heart Failure',
    status: 'Active',
    documents: 287,
    complianceScore: 91.8,
    sites: 32,
    enrolledPatients: 480,
    startDate: '2025-06-01',
    estimatedEndDate: '2027-12-15',
    principalInvestigator: 'Dr. Michael Torres',
  },
  {
    id: 'TG-2025-1102',
    sponsor: 'Roche/Genentech',
    protocolNumber: 'GNE-TAU-1102',
    title: 'Anti-Tau Antibody Therapy in Early-Stage Alzheimer\'s Disease',
    phase: 'Phase II',
    therapeuticArea: 'Neurology',
    indication: 'Alzheimer\'s Disease',
    status: 'Active',
    documents: 198,
    complianceScore: 97.1,
    sites: 24,
    enrolledPatients: 360,
    startDate: '2025-01-10',
    estimatedEndDate: '2027-06-30',
    principalInvestigator: 'Dr. Emily Nakamura',
  },
  {
    id: 'TG-2026-0391',
    sponsor: 'AstraZeneca',
    protocolNumber: 'AZN-DARE-0391',
    title: 'Durvalumab + Novel ADC Combination in Triple-Negative Breast Cancer',
    phase: 'Phase III',
    therapeuticArea: 'Oncology',
    indication: 'Triple-Negative Breast Cancer',
    status: 'Active',
    documents: 456,
    complianceScore: 88.5,
    sites: 64,
    enrolledPatients: 2100,
    startDate: '2025-09-01',
    estimatedEndDate: '2028-03-31',
    principalInvestigator: 'Dr. Rachel Hoffman',
  },
  {
    id: 'TG-2025-0744',
    sponsor: 'Eli Lilly',
    protocolNumber: 'LLY-GLP1-0744',
    title: 'Tirzepatide Long-Term Cardiovascular Outcomes Study',
    phase: 'Phase IV',
    therapeuticArea: 'Endocrinology',
    indication: 'Type 2 Diabetes / Obesity',
    status: 'Active',
    documents: 521,
    complianceScore: 96.3,
    sites: 72,
    enrolledPatients: 3400,
    startDate: '2025-04-20',
    estimatedEndDate: '2029-04-20',
    principalInvestigator: 'Dr. James Liu',
  },
  {
    id: 'TG-2024-1538',
    sponsor: 'Merck & Co.',
    protocolNumber: 'MRK-KN966-1538',
    title: 'KEYTRUDA + Favezelimab in Relapsed/Refractory Classical Hodgkin Lymphoma',
    phase: 'Phase III',
    therapeuticArea: 'Oncology',
    indication: 'Hodgkin Lymphoma',
    status: 'Completed',
    documents: 389,
    complianceScore: 99.1,
    sites: 38,
    enrolledPatients: 890,
    startDate: '2024-02-01',
    estimatedEndDate: '2026-02-28',
    principalInvestigator: 'Dr. David Park',
  },
  {
    id: 'TG-2026-0156',
    sponsor: 'Sanofi',
    protocolNumber: 'SNF-DPX-0156',
    title: 'Dupixent in Moderate-to-Severe Chronic Rhinosinusitis with Nasal Polyps',
    phase: 'Phase III',
    therapeuticArea: 'Immunology',
    indication: 'Chronic Rhinosinusitis',
    status: 'On Hold',
    documents: 142,
    complianceScore: 82.4,
    sites: 18,
    enrolledPatients: 210,
    startDate: '2026-01-15',
    estimatedEndDate: '2028-01-15',
    principalInvestigator: 'Dr. Anna Petrova',
  },
  {
    id: 'TG-2024-0923',
    sponsor: 'Johnson & Johnson',
    protocolNumber: 'JNJ-CAR-T-0923',
    title: 'Carvykti CAR-T Cell Therapy in Earlier Lines of Multiple Myeloma',
    phase: 'Phase II',
    therapeuticArea: 'Oncology',
    indication: 'Multiple Myeloma',
    status: 'Archived',
    documents: 267,
    complianceScore: 95.7,
    sites: 28,
    enrolledPatients: 540,
    startDate: '2024-05-10',
    estimatedEndDate: '2026-05-10',
    principalInvestigator: 'Dr. Robert Kim',
  },
];

export const documents: Document[] = [
  { id: 'DOC-001', name: 'Protocol v3.2 - PF-07321332-0847', studyId: 'TG-2026-0847', type: 'Protocol', version: '3.2', status: 'Validated', uploadedBy: 'Dr. Sarah Chen', uploadedAt: '2026-05-18T14:30:00Z', size: '4.2 MB', language: 'English', site: 'All Sites', findings: 2 },
  { id: 'DOC-002', name: 'Informed Consent Form - Site 012', studyId: 'TG-2026-0847', type: 'ICF', version: '2.1', status: 'Validated', uploadedBy: 'Jennifer Morris', uploadedAt: '2026-05-17T09:15:00Z', size: '1.8 MB', language: 'English', site: 'Site 012 - Mayo Clinic', findings: 0 },
  { id: 'DOC-003', name: 'Investigator\'s Brochure - Edition 7', studyId: 'TG-2026-0847', type: 'IB', version: '7.0', status: 'Pending', uploadedBy: 'Mark Thompson', uploadedAt: '2026-05-19T11:00:00Z', size: '12.5 MB', language: 'English', site: 'All Sites', findings: 0 },
  { id: 'DOC-004', name: 'SAE Report - Subject 0847-012-0034', studyId: 'TG-2026-0847', type: 'SAE Report', version: '1.0', status: 'In Review', uploadedBy: 'Dr. Lisa Wang', uploadedAt: '2026-05-20T08:45:00Z', size: '856 KB', language: 'English', site: 'Site 012 - Mayo Clinic', findings: 3 },
  { id: 'DOC-005', name: 'Clinical Study Report - Draft', studyId: 'TG-2024-1538', type: 'CSR', version: '0.9', status: 'In Review', uploadedBy: 'Dr. David Park', uploadedAt: '2026-05-15T16:20:00Z', size: '28.3 MB', language: 'English', site: 'All Sites', findings: 8 },
  { id: 'DOC-006', name: 'Site Monitoring Visit Report - Site 007', studyId: 'TG-2026-0623', type: 'Monitoring Report', version: '1.0', status: 'Validated', uploadedBy: 'Angela Rivera', uploadedAt: '2026-05-16T13:10:00Z', size: '2.1 MB', language: 'English', site: 'Site 007 - Cleveland Clinic', findings: 1 },
  { id: 'DOC-007', name: 'Statistical Analysis Plan v2.0', studyId: 'TG-2025-0744', type: 'SAP', version: '2.0', status: 'Validated', uploadedBy: 'Dr. James Liu', uploadedAt: '2026-05-14T10:30:00Z', size: '3.7 MB', language: 'English', site: 'All Sites', findings: 0 },
  { id: 'DOC-008', name: 'Case Report Form - Visit Schedule', studyId: 'TG-2026-0391', type: 'CRF', version: '1.3', status: 'Failed', uploadedBy: 'Karen O\'Brien', uploadedAt: '2026-05-19T15:45:00Z', size: '5.6 MB', language: 'English', site: 'All Sites', findings: 12 },
  { id: 'DOC-009', name: 'IRB Approval Letter - Central', studyId: 'TG-2025-1102', type: 'IRB Approval', version: '1.0', status: 'Validated', uploadedBy: 'Compliance Team', uploadedAt: '2026-05-12T09:00:00Z', size: '420 KB', language: 'English', site: 'Central', findings: 0 },
  { id: 'DOC-010', name: 'Data Safety Monitoring Board Charter', studyId: 'TG-2026-0847', type: 'DSMB Charter', version: '1.1', status: 'Validated', uploadedBy: 'Dr. Sarah Chen', uploadedAt: '2026-05-10T14:00:00Z', size: '1.2 MB', language: 'English', site: 'All Sites', findings: 1 },
];

export const findings: Finding[] = [
  {
    id: 'FND-001',
    documentId: 'DOC-008',
    documentName: 'Case Report Form - Visit Schedule',
    studyId: 'TG-2026-0391',
    title: 'Missing Primary Endpoint Definition in CRF',
    description: 'The Case Report Form does not include a clear definition of the primary endpoint measurement schedule. Visit 4 and Visit 6 data collection forms lack the required PFS assessment fields as specified in Protocol Section 8.2.',
    severity: 'critical',
    category: 'Protocol Deviation',
    agentSource: 'Protocol Compliance Agent',
    confidenceScore: 96,
    regulatoryReference: 'ICH E6(R3) Section 6.4.9',
    suggestedRemediation: 'Update CRF to include PFS assessment fields at Visit 4 (Week 12) and Visit 6 (Week 24) as specified in the approved protocol. Ensure alignment with Statistical Analysis Plan v2.0.',
    status: 'Open',
    createdAt: '2026-05-19T15:50:00Z',
  },
  {
    id: 'FND-002',
    documentId: 'DOC-004',
    documentName: 'SAE Report - Subject 0847-012-0034',
    studyId: 'TG-2026-0847',
    title: 'SAE Reporting Timeline Non-Compliance',
    description: 'The Serious Adverse Event report for Subject 0847-012-0034 was submitted 28 days after the initial event awareness date. Regulatory requirement mandates submission within 24 hours for fatal/life-threatening events and 15 days for all other SAEs.',
    severity: 'critical',
    category: 'Safety Reporting',
    agentSource: 'Safety & Pharmacovigilance Agent',
    confidenceScore: 99,
    regulatoryReference: 'ICH E2A, 21 CFR 312.32',
    suggestedRemediation: 'Immediately file a late SAE notification with the FDA and all participating IRBs. Initiate CAPA for the site and retrain site personnel on SAE reporting timelines.',
    status: 'Escalated',
    createdAt: '2026-05-20T09:00:00Z',
  },
  {
    id: 'FND-003',
    documentId: 'DOC-005',
    documentName: 'Clinical Study Report - Draft',
    studyId: 'TG-2024-1538',
    title: 'Inconsistent Efficacy Data Between CSR Tables',
    description: 'Table 14.2.1 (Primary Efficacy Analysis) reports an ORR of 78.4% while Table 14.2.4 (Subgroup Analysis) calculates ORR at 76.1% for the same ITT population. This 2.3% discrepancy suggests a data extraction or calculation error.',
    severity: 'major',
    category: 'Data Integrity',
    agentSource: 'Medical Writing & Consistency Agent',
    confidenceScore: 94,
    regulatoryReference: 'ICH E3 Section 11.4',
    suggestedRemediation: 'Reconcile efficacy data between all CSR tables. Verify source datasets in the SDTM/ADaM domains and regenerate tables using the validated SAS programs.',
    status: 'Open',
    createdAt: '2026-05-15T16:35:00Z',
  },
  {
    id: 'FND-004',
    documentId: 'DOC-001',
    documentName: 'Protocol v3.2 - PF-07321332-0847',
    studyId: 'TG-2026-0847',
    title: 'Inclusion Criteria Age Range Conflicts with Synopsis',
    description: 'Protocol Section 5.1 states inclusion criteria as "≥18 to ≤75 years" while the Protocol Synopsis on page 3 states "≥18 to ≤80 years". This inconsistency could lead to enrollment of ineligible subjects.',
    severity: 'major',
    category: 'Protocol Consistency',
    agentSource: 'Protocol Compliance Agent',
    confidenceScore: 98,
    regulatoryReference: 'ICH E6(R3) Section 6.5',
    suggestedRemediation: 'Issue a protocol clarification memo and determine the correct age range. If a protocol amendment is needed, follow the amendment process per SOP-CL-004.',
    status: 'Open',
    createdAt: '2026-05-18T14:45:00Z',
  },
  {
    id: 'FND-005',
    documentId: 'DOC-008',
    documentName: 'Case Report Form - Visit Schedule',
    studyId: 'TG-2026-0391',
    title: 'Missing CTCAE v5.0 Grading Scale Reference',
    description: 'Adverse event reporting section of the CRF references CTCAE v4.03 grading criteria. The study protocol mandates use of CTCAE v5.0 for all safety assessments.',
    severity: 'major',
    category: 'Protocol Deviation',
    agentSource: 'Regulatory Intelligence Agent',
    confidenceScore: 92,
    regulatoryReference: 'ICH E6(R3) Section 6.12',
    suggestedRemediation: 'Update CRF to reference CTCAE v5.0 grading scale. Review all previously collected AE data for potential regrading under the correct version.',
    status: 'Open',
    createdAt: '2026-05-19T16:00:00Z',
  },
  {
    id: 'FND-006',
    documentId: 'DOC-006',
    documentName: 'Site Monitoring Visit Report - Site 007',
    studyId: 'TG-2026-0623',
    title: 'Source Data Verification Gap Identified',
    description: 'Monitoring report indicates only 42% of critical data points were source-verified during the visit, below the required 100% SDV threshold for the first 20 subjects per site.',
    severity: 'minor',
    category: 'Monitoring',
    agentSource: 'TMF Completeness Agent',
    confidenceScore: 87,
    regulatoryReference: 'ICH E6(R3) Section 5.18.4',
    suggestedRemediation: 'Schedule a follow-up targeted SDV visit to complete verification of remaining critical data points for the first 20 subjects at Site 007.',
    status: 'Open',
    createdAt: '2026-05-16T13:25:00Z',
  },
  {
    id: 'FND-007',
    documentId: 'DOC-005',
    documentName: 'Clinical Study Report - Draft',
    studyId: 'TG-2024-1538',
    title: 'Appendix 16.1.1 Missing Signed Protocol',
    description: 'CSR Appendix 16.1.1 should contain the signed final protocol and all amendments. Currently contains unsigned draft protocol version 4.1 instead of signed version 5.0.',
    severity: 'minor',
    category: 'Document Completeness',
    agentSource: 'TMF Completeness Agent',
    confidenceScore: 91,
    regulatoryReference: 'ICH E3 Section 16.1',
    suggestedRemediation: 'Replace draft protocol in Appendix 16.1.1 with the final signed protocol v5.0 and include all signed amendments.',
    status: 'Resolved',
    createdAt: '2026-05-15T17:00:00Z',
  },
  {
    id: 'FND-008',
    documentId: 'DOC-010',
    documentName: 'Data Safety Monitoring Board Charter',
    studyId: 'TG-2026-0847',
    title: 'DSMB Voting Procedures Lack Quorum Definition',
    description: 'The DSMB Charter Section 4.3 describes voting procedures but does not define the minimum number of members required for a quorum. This could impact the validity of DSMB recommendations.',
    severity: 'minor',
    category: 'Governance',
    agentSource: 'Regulatory Intelligence Agent',
    confidenceScore: 85,
    regulatoryReference: 'FDA Guidance: Establishment and Operation of Clinical Trial DSMBs',
    suggestedRemediation: 'Add a quorum definition to Section 4.3 of the DSMB Charter. Recommend requiring at least 2/3 of voting members for all efficacy and safety decisions.',
    status: 'Open',
    createdAt: '2026-05-10T14:15:00Z',
  },
  {
    id: 'FND-009',
    documentId: 'DOC-003',
    documentName: 'Investigator\'s Brochure - Edition 7',
    studyId: 'TG-2026-0847',
    title: 'IB Pharmacokinetics Section Uses Outdated Reference Data',
    description: 'Section 5.3 of the IB cites Phase I PK data from 2022 but does not incorporate the updated population PK model results from the Phase II study completed in Q4 2025.',
    severity: 'info',
    category: 'Scientific Content',
    agentSource: 'Medical Writing & Consistency Agent',
    confidenceScore: 78,
    regulatoryReference: 'ICH E7, ICH M4E',
    suggestedRemediation: 'Consider updating IB Section 5.3 with the latest population PK model results. This is recommended but not required for the current edition.',
    status: 'Open',
    createdAt: '2026-05-19T11:20:00Z',
  },
  {
    id: 'FND-010',
    documentId: 'DOC-002',
    documentName: 'Informed Consent Form - Site 012',
    studyId: 'TG-2026-0847',
    title: 'Consent Form Reading Level Assessment',
    description: 'The ICF scores at a Flesch-Kincaid Grade Level of 12.8, which exceeds the recommended 8th grade reading level for informed consent documents. This may impact subject comprehension.',
    severity: 'info',
    category: 'Patient Communications',
    agentSource: 'Medical Writing & Consistency Agent',
    confidenceScore: 82,
    regulatoryReference: 'FDA 21 CFR 50.25',
    suggestedRemediation: 'Revise the ICF to reduce the Flesch-Kincaid Grade Level to 8.0 or below. Focus on simplifying medical terminology in Sections 3, 5, and 7.',
    status: 'Open',
    createdAt: '2026-05-17T09:30:00Z',
  },
  {
    id: 'FND-011',
    documentId: 'DOC-008',
    documentName: 'Case Report Form - Visit Schedule',
    studyId: 'TG-2026-0391',
    title: 'Lab Panel Missing Hepatic Function Tests',
    description: 'The central laboratory panel in the CRF Visit 3 schedule does not include ALT, AST, and bilirubin assessments despite the protocol requirement for hepatic function monitoring every 4 weeks.',
    severity: 'critical',
    category: 'Patient Safety',
    agentSource: 'Safety & Pharmacovigilance Agent',
    confidenceScore: 97,
    regulatoryReference: 'ICH E6(R3) Section 4.5, FDA Drug-Induced Liver Injury Guidance',
    suggestedRemediation: 'Urgently add hepatic function panel (ALT, AST, total bilirubin, ALP) to Visit 3 CRF. Review if any subjects have missed hepatic assessments and arrange catch-up testing.',
    status: 'Open',
    createdAt: '2026-05-19T16:10:00Z',
  },
  {
    id: 'FND-012',
    documentId: 'DOC-005',
    documentName: 'Clinical Study Report - Draft',
    studyId: 'TG-2024-1538',
    title: 'Subject Disposition Flowchart Arithmetic Error',
    description: 'The CONSORT flow diagram in Section 10.1 shows 892 randomized subjects but the sum of treatment arms equals 888 (444 + 444). Four subjects are unaccounted for in the disposition.',
    severity: 'major',
    category: 'Data Integrity',
    agentSource: 'Cross-Reference Validator Agent',
    confidenceScore: 99,
    regulatoryReference: 'ICH E3 Section 10.1, CONSORT Statement',
    suggestedRemediation: 'Verify the randomization database and account for all 892 subjects. Update the CONSORT diagram and all related disposition tables.',
    status: 'Open',
    createdAt: '2026-05-15T16:50:00Z',
  },
];

export const validationRuns: ValidationRun[] = [
  { id: 'VR-001', documentName: 'Case Report Form - Visit Schedule', studyId: 'TG-2026-0391', status: 'Running', agentsCompleted: 4, totalAgents: 7, startedAt: '2026-05-20T15:30:00Z', duration: '3m 42s', findingsCount: 5 },
  { id: 'VR-002', documentName: 'SAE Report - Subject 0847-012-0034', studyId: 'TG-2026-0847', status: 'Completed', agentsCompleted: 7, totalAgents: 7, startedAt: '2026-05-20T14:15:00Z', duration: '8m 15s', findingsCount: 3 },
  { id: 'VR-003', documentName: 'Investigator\'s Brochure - Edition 7', studyId: 'TG-2026-0847', status: 'Pending', agentsCompleted: 0, totalAgents: 7, startedAt: '2026-05-20T15:45:00Z', duration: '--', findingsCount: 0 },
  { id: 'VR-004', documentName: 'Clinical Study Report - Draft', studyId: 'TG-2024-1538', status: 'Completed', agentsCompleted: 7, totalAgents: 7, startedAt: '2026-05-20T10:00:00Z', duration: '22m 04s', findingsCount: 8 },
  { id: 'VR-005', documentName: 'Protocol v3.2 - PF-07321332-0847', studyId: 'TG-2026-0847', status: 'Completed', agentsCompleted: 7, totalAgents: 7, startedAt: '2026-05-19T16:00:00Z', duration: '12m 38s', findingsCount: 2 },
  { id: 'VR-006', documentName: 'Site Monitoring Visit Report - Site 007', studyId: 'TG-2026-0623', status: 'Completed', agentsCompleted: 7, totalAgents: 7, startedAt: '2026-05-18T11:30:00Z', duration: '6m 52s', findingsCount: 1 },
  { id: 'VR-007', documentName: 'Statistical Analysis Plan v2.0', studyId: 'TG-2025-0744', status: 'Completed', agentsCompleted: 7, totalAgents: 7, startedAt: '2026-05-17T09:45:00Z', duration: '9m 11s', findingsCount: 0 },
  { id: 'VR-008', documentName: 'Informed Consent Form - Site 012', studyId: 'TG-2026-0847', status: 'Completed', agentsCompleted: 7, totalAgents: 7, startedAt: '2026-05-17T14:00:00Z', duration: '5m 27s', findingsCount: 0 },
];

export const auditEntries: AuditEntry[] = [
  { id: 'AUD-001', timestamp: '2026-05-20T15:45:00Z', user: 'Dr. Sarah Chen', action: 'Upload Document', entity: 'Investigator\'s Brochure - Edition 7', entityType: 'Document', details: 'Uploaded new version (v7.0) of the Investigator Brochure for study TG-2026-0847', ipAddress: '10.128.45.102' },
  { id: 'AUD-002', timestamp: '2026-05-20T15:30:00Z', user: 'System', action: 'Start Validation', entity: 'Case Report Form - Visit Schedule', entityType: 'Validation', details: 'Initiated automated validation pipeline for CRF document DOC-008', ipAddress: 'System' },
  { id: 'AUD-003', timestamp: '2026-05-20T14:15:00Z', user: 'System', action: 'Complete Validation', entity: 'SAE Report - Subject 0847-012-0034', entityType: 'Validation', details: 'Validation completed with 3 findings (2 critical, 1 major)', ipAddress: 'System' },
  { id: 'AUD-004', timestamp: '2026-05-20T10:30:00Z', user: 'Jennifer Morris', action: 'Escalate Finding', entity: 'FND-002', entityType: 'Finding', details: 'Escalated SAE timeline non-compliance finding to Chief Medical Officer', ipAddress: '10.128.45.87' },
  { id: 'AUD-005', timestamp: '2026-05-20T09:15:00Z', user: 'Mark Thompson', action: 'Resolve Finding', entity: 'FND-007', entityType: 'Finding', details: 'Resolved CSR appendix finding - signed protocol v5.0 now included', ipAddress: '10.128.45.215' },
  { id: 'AUD-006', timestamp: '2026-05-19T16:30:00Z', user: 'System', action: 'Agent Error', entity: 'Cross-Reference Validator', entityType: 'Agent', details: 'Agent timeout during CSR cross-reference validation. Auto-recovered after 45 seconds.', ipAddress: 'System' },
  { id: 'AUD-007', timestamp: '2026-05-19T14:00:00Z', user: 'Angela Rivera', action: 'Export Report', entity: 'Compliance Summary - TG-2026-0623', entityType: 'Report', details: 'Exported compliance summary report in PDF format for sponsor review', ipAddress: '10.128.45.156' },
  { id: 'AUD-008', timestamp: '2026-05-19T11:00:00Z', user: 'Admin', action: 'Update Configuration', entity: 'Safety & Pharmacovigilance Agent', entityType: 'Agent', details: 'Updated SAE detection sensitivity threshold from 0.85 to 0.90', ipAddress: '10.128.45.1' },
  { id: 'AUD-009', timestamp: '2026-05-18T16:45:00Z', user: 'Dr. Rachel Hoffman', action: 'Create Study', entity: 'TG-2026-0391', entityType: 'Study', details: 'Created new study record for AstraZeneca Durvalumab + ADC trial', ipAddress: '10.128.45.198' },
  { id: 'AUD-010', timestamp: '2026-05-18T09:30:00Z', user: 'System', action: 'Backup Complete', entity: 'System Database', entityType: 'System', details: 'Automated daily backup completed successfully. 2.3 GB compressed.', ipAddress: 'System' },
];

export const agentStatuses: AgentStatus[] = [
  {
    id: 'agent-1',
    name: 'Protocol Compliance Agent',
    description: 'Validates documents against study protocol requirements and ICH/GCP guidelines',
    status: 'running',
    uptime: '99.97%',
    tasksCompleted: 1247,
    avgProcessingTime: '2m 34s',
    errorRate: 0.3,
    lastActive: '2026-05-20T15:48:00Z',
    circuitBreaker: 'closed',
    queueDepth: 3,
    sparklineData: [45, 52, 48, 61, 55, 58, 62, 59, 54, 67, 63, 58],
  },
  {
    id: 'agent-2',
    name: 'Safety & Pharmacovigilance Agent',
    description: 'Monitors safety reporting compliance, SAE timelines, and CIOMS form accuracy',
    status: 'running',
    uptime: '99.99%',
    tasksCompleted: 893,
    avgProcessingTime: '3m 12s',
    errorRate: 0.1,
    lastActive: '2026-05-20T15:47:00Z',
    circuitBreaker: 'closed',
    queueDepth: 1,
    sparklineData: [32, 38, 35, 42, 40, 37, 44, 41, 39, 45, 43, 40],
  },
  {
    id: 'agent-3',
    name: 'TMF Completeness Agent',
    description: 'Checks Trial Master File zone completeness against DIA Reference Model v3.3',
    status: 'idle',
    uptime: '99.92%',
    tasksCompleted: 2156,
    avgProcessingTime: '1m 48s',
    errorRate: 0.8,
    lastActive: '2026-05-20T15:30:00Z',
    circuitBreaker: 'closed',
    queueDepth: 0,
    sparklineData: [78, 82, 75, 89, 85, 91, 88, 84, 92, 87, 90, 86],
  },
  {
    id: 'agent-4',
    name: 'Regulatory Intelligence Agent',
    description: 'Cross-references documents against FDA, EMA, and PMDA regulatory requirements',
    status: 'running',
    uptime: '99.85%',
    tasksCompleted: 1034,
    avgProcessingTime: '4m 05s',
    errorRate: 1.5,
    lastActive: '2026-05-20T15:49:00Z',
    circuitBreaker: 'closed',
    queueDepth: 2,
    sparklineData: [28, 33, 30, 37, 35, 31, 39, 36, 34, 41, 38, 35],
  },
  {
    id: 'agent-5',
    name: 'Medical Writing & Consistency Agent',
    description: 'Checks document consistency, terminology, cross-references, and writing quality',
    status: 'completed',
    uptime: '99.91%',
    tasksCompleted: 1578,
    avgProcessingTime: '2m 56s',
    errorRate: 0.9,
    lastActive: '2026-05-20T15:40:00Z',
    circuitBreaker: 'closed',
    queueDepth: 0,
    sparklineData: [55, 60, 58, 65, 62, 68, 64, 61, 70, 66, 72, 68],
  },
  {
    id: 'agent-6',
    name: 'Cross-Reference Validator Agent',
    description: 'Validates cross-references between documents, tables, figures, and appendices',
    status: 'error',
    uptime: '98.45%',
    tasksCompleted: 967,
    avgProcessingTime: '5m 22s',
    errorRate: 3.2,
    lastActive: '2026-05-20T15:15:00Z',
    circuitBreaker: 'half-open',
    queueDepth: 5,
    sparklineData: [22, 25, 28, 18, 15, 8, 12, 20, 24, 16, 10, 14],
  },
  {
    id: 'agent-7',
    name: 'Submission Readiness Agent',
    description: 'Assesses overall submission readiness for eCTD and regional regulatory submissions',
    status: 'idle',
    uptime: '99.88%',
    tasksCompleted: 456,
    avgProcessingTime: '6m 15s',
    errorRate: 0.5,
    lastActive: '2026-05-20T14:50:00Z',
    circuitBreaker: 'closed',
    queueDepth: 0,
    sparklineData: [15, 18, 16, 22, 20, 25, 23, 19, 27, 24, 28, 26],
  },
];

export const tmfZones: TMFZone[] = [
  {
    id: 'zone-01',
    name: 'Trial Management',
    zoneNumber: 1,
    completeness: 92,
    totalArtifacts: 28,
    completedArtifacts: 26,
    sections: [
      { id: 'z1-s1', name: 'Trial Oversight', artifacts: [
        { id: 'z1-a1', name: 'Trial Master Plan', present: true, validated: true, lastUpdated: '2026-04-15' },
        { id: 'z1-a2', name: 'Project Plan', present: true, validated: true, lastUpdated: '2026-03-20' },
        { id: 'z1-a3', name: 'Communication Plan', present: true, validated: false, lastUpdated: '2026-02-10' },
      ]},
      { id: 'z1-s2', name: 'Trial Team', artifacts: [
        { id: 'z1-a4', name: 'Team Contact List', present: true, validated: true, lastUpdated: '2026-05-01' },
        { id: 'z1-a5', name: 'Delegation Log', present: true, validated: true, lastUpdated: '2026-05-10' },
        { id: 'z1-a6', name: 'Training Records', present: false, validated: false },
      ]},
    ],
  },
  {
    id: 'zone-02',
    name: 'Central Trial Documents',
    zoneNumber: 2,
    completeness: 96,
    totalArtifacts: 35,
    completedArtifacts: 34,
    sections: [
      { id: 'z2-s1', name: 'Protocol', artifacts: [
        { id: 'z2-a1', name: 'Final Protocol', present: true, validated: true, lastUpdated: '2026-05-18' },
        { id: 'z2-a2', name: 'Protocol Amendments', present: true, validated: true, lastUpdated: '2026-04-22' },
        { id: 'z2-a3', name: 'Protocol Synopsis', present: true, validated: true, lastUpdated: '2026-05-18' },
      ]},
      { id: 'z2-s2', name: 'Investigator Brochure', artifacts: [
        { id: 'z2-a4', name: 'Current IB', present: true, validated: true, lastUpdated: '2026-05-19' },
        { id: 'z2-a5', name: 'IB Supplements', present: true, validated: false, lastUpdated: '2026-03-15' },
      ]},
    ],
  },
  {
    id: 'zone-03',
    name: 'Regulatory',
    zoneNumber: 3,
    completeness: 88,
    totalArtifacts: 22,
    completedArtifacts: 19,
    sections: [
      { id: 'z3-s1', name: 'Regulatory Applications', artifacts: [
        { id: 'z3-a1', name: 'IND Application', present: true, validated: true, lastUpdated: '2025-03-01' },
        { id: 'z3-a2', name: 'FDA Correspondence', present: true, validated: true, lastUpdated: '2026-04-30' },
        { id: 'z3-a3', name: 'EMA Submission', present: false, validated: false },
      ]},
    ],
  },
  {
    id: 'zone-04',
    name: 'IRB/IEC',
    zoneNumber: 4,
    completeness: 100,
    totalArtifacts: 18,
    completedArtifacts: 18,
    sections: [
      { id: 'z4-s1', name: 'Approvals', artifacts: [
        { id: 'z4-a1', name: 'Central IRB Approval', present: true, validated: true, lastUpdated: '2026-05-12' },
        { id: 'z4-a2', name: 'Informed Consent Forms', present: true, validated: true, lastUpdated: '2026-05-17' },
        { id: 'z4-a3', name: 'IRB Correspondence', present: true, validated: true, lastUpdated: '2026-05-05' },
      ]},
    ],
  },
  {
    id: 'zone-05',
    name: 'Site Management',
    zoneNumber: 5,
    completeness: 85,
    totalArtifacts: 32,
    completedArtifacts: 27,
    sections: [
      { id: 'z5-s1', name: 'Site Selection', artifacts: [
        { id: 'z5-a1', name: 'Feasibility Reports', present: true, validated: true, lastUpdated: '2025-01-15' },
        { id: 'z5-a2', name: 'Pre-Study Visit Reports', present: true, validated: true, lastUpdated: '2025-02-20' },
        { id: 'z5-a3', name: 'Site Contracts', present: true, validated: false, lastUpdated: '2025-03-10' },
      ]},
    ],
  },
  {
    id: 'zone-06',
    name: 'Investigational Product',
    zoneNumber: 6,
    completeness: 94,
    totalArtifacts: 20,
    completedArtifacts: 19,
    sections: [
      { id: 'z6-s1', name: 'IP Management', artifacts: [
        { id: 'z6-a1', name: 'IP Accountability Logs', present: true, validated: true, lastUpdated: '2026-05-15' },
        { id: 'z6-a2', name: 'Certificate of Analysis', present: true, validated: true, lastUpdated: '2026-04-20' },
        { id: 'z6-a3', name: 'Shipping Records', present: true, validated: true, lastUpdated: '2026-05-18' },
      ]},
    ],
  },
  {
    id: 'zone-07',
    name: 'Safety Reporting',
    zoneNumber: 7,
    completeness: 78,
    totalArtifacts: 25,
    completedArtifacts: 19,
    sections: [
      { id: 'z7-s1', name: 'Safety Reports', artifacts: [
        { id: 'z7-a1', name: 'SAE Reports', present: true, validated: false, lastUpdated: '2026-05-20' },
        { id: 'z7-a2', name: 'DSUR/PBRER', present: true, validated: true, lastUpdated: '2026-03-31' },
        { id: 'z7-a3', name: 'DSMB Reports', present: false, validated: false },
        { id: 'z7-a4', name: 'Safety Narratives', present: false, validated: false },
      ]},
    ],
  },
  {
    id: 'zone-08',
    name: 'Central & Local Testing',
    zoneNumber: 8,
    completeness: 91,
    totalArtifacts: 15,
    completedArtifacts: 14,
    sections: [
      { id: 'z8-s1', name: 'Laboratory', artifacts: [
        { id: 'z8-a1', name: 'Lab Certification', present: true, validated: true, lastUpdated: '2026-01-15' },
        { id: 'z8-a2', name: 'Normal Ranges', present: true, validated: true, lastUpdated: '2026-01-15' },
        { id: 'z8-a3', name: 'Lab Manual', present: true, validated: true, lastUpdated: '2025-12-01' },
      ]},
    ],
  },
  {
    id: 'zone-09',
    name: 'Third Parties',
    zoneNumber: 9,
    completeness: 87,
    totalArtifacts: 12,
    completedArtifacts: 10,
    sections: [
      { id: 'z9-s1', name: 'Vendor Management', artifacts: [
        { id: 'z9-a1', name: 'Vendor Contracts', present: true, validated: true, lastUpdated: '2025-06-15' },
        { id: 'z9-a2', name: 'Vendor Audits', present: true, validated: false, lastUpdated: '2026-02-28' },
        { id: 'z9-a3', name: 'Vendor Certifications', present: false, validated: false },
      ]},
    ],
  },
  {
    id: 'zone-10',
    name: 'Data Management',
    zoneNumber: 10,
    completeness: 95,
    totalArtifacts: 18,
    completedArtifacts: 17,
    sections: [
      { id: 'z10-s1', name: 'Data Plans', artifacts: [
        { id: 'z10-a1', name: 'Data Management Plan', present: true, validated: true, lastUpdated: '2026-04-10' },
        { id: 'z10-a2', name: 'Database Design', present: true, validated: true, lastUpdated: '2026-03-25' },
        { id: 'z10-a3', name: 'Edit Check Plan', present: true, validated: true, lastUpdated: '2026-04-05' },
      ]},
    ],
  },
  {
    id: 'zone-11',
    name: 'Statistics',
    zoneNumber: 11,
    completeness: 90,
    totalArtifacts: 14,
    completedArtifacts: 13,
    sections: [
      { id: 'z11-s1', name: 'Statistical Documents', artifacts: [
        { id: 'z11-a1', name: 'Statistical Analysis Plan', present: true, validated: true, lastUpdated: '2026-05-14' },
        { id: 'z11-a2', name: 'Randomization Plan', present: true, validated: true, lastUpdated: '2025-03-01' },
        { id: 'z11-a3', name: 'Sample Size Justification', present: true, validated: true, lastUpdated: '2025-02-15' },
      ]},
    ],
  },
];
