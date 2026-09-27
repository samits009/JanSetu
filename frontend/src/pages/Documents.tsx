import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useI18n } from '../i18n/I18nContext';
import { documentApi } from '../services/documentApi';
import { DocumentDetailResponse, DocumentResponse } from '../domain/models';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import {
  GlassCard,
  GlassButton,
  GlassSelect,
  StatusPill,
  ProgressGlow,
  EvidenceGraph,
  WelfareMetric,
  DocumentCard,
} from '../components/common';

export function Documents() {
  const { currentCitizenId } = useAuth();
  const { language } = useI18n();
  const navigate = useNavigate();
  const [docs, setDocs] = useState<DocumentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [processingStage, setProcessingStage] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<Error | null>(null);
  const [documentType, setDocumentType] = useState('BOCW_CARD');
  const fileInput = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (currentCitizenId) {
      loadDocuments();
    }
  }, [currentCitizenId]);

  const loadDocuments = () => {
    setLoading(true);
    documentApi
      .listDocuments(currentCitizenId)
      .then(setDocs)
      .catch(setError)
      .finally(() => setLoading(false));
  };

  const uploadDocument = async (file?: File) => {
    if (!file) return;
    setUploadError(null);

    // Real network and extraction progression
    setProcessingStage('Uploading');

    try {
      setProcessingStage('Processing & Extracting');
      await documentApi.uploadDocument(currentCitizenId, documentType, file);
      await loadDocuments();
      setProcessingStage('Evidence Ready');
    } catch (err) {
      setUploadError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setTimeout(() => {
        setProcessingStage(null);
        if (fileInput.current) fileInput.current.value = '';
      }, 1200);
    }
  };

  const verifiedCount = docs.filter((d) => d.verification_status === 'VERIFIED').length;
  const readinessPercent = docs.length > 0 ? Math.round((verifiedCount / docs.length) * 100) : 0;

  return (
    <div className="stack">
      {/* 1. Top Evidence Vault Header with Large Readiness Gauge */}
      <GlassCard variant="hero">
        <span className="status-pill status-pill-gold status-pill-sm" style={{ marginBottom: 8 }}>
          ✦ SOVEREIGN EVIDENCE VAULT
        </span>
        <h1 style={{ fontSize: 24 }}>
          {language === 'hi' ? 'आपके दस्तावेज़ एवं साक्ष्य' : 'Your Documents'}
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13.5, margin: '4px 0 18px' }}>
          {language === 'hi'
            ? 'सत्यापित साक्ष्य का उपयोग केंद्रीय और राज्य की सभी योजनाओं में स्वतः किया जाता है।'
            : 'Verified statutory facts extracted from your documents, securely reusable across every welfare program.'}
        </p>

        {/* Large Readiness Gauge */}
        <div style={{ background: 'rgba(255,255,255,0.04)', padding: '16px 20px', borderRadius: 18, border: '1px solid rgba(255,255,255,0.08)' }}>
          <ProgressGlow
            value={readinessPercent}
            tone="gold"
            size="lg"
            showLabel={true}
            label={language === 'hi' ? 'कुल साक्ष्य तत्परता' : 'Overall Evidence Readiness'}
          />
        </div>

        {/* Vault Metric Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginTop: 14 }}>
          <WelfareMetric
            label={language === 'hi' ? 'कुल दस्तावेज़' : 'Documents'}
            value={docs.length}
            tone="blue"
          />
          <WelfareMetric
            label={language === 'hi' ? 'सत्यापित साक्ष्य' : 'Verified'}
            value={verifiedCount}
            tone="emerald"
          />
          <WelfareMetric
            label={language === 'hi' ? 'दावे' : 'Claims'}
            value={docs.reduce((acc, d) => acc + Object.keys(d.extracted_data || {}).length, 0)}
            tone="gold"
          />
        </div>
      </GlassCard>

      {/* 2. Visual Document Processing Progression: Uploaded → Processing → Extracting → Evidence Ready */}
      {processingStage && (
        <GlassCard variant="luminous" style={{ padding: '16px 20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--gold-primary)' }}>
              DOCUMENT INTELLIGENCE PIPELINE
            </span>
            <span className="glass-btn-spinner" />
          </div>

          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            {['Uploaded', 'Processing', 'Extracting', 'Evidence Ready'].map((stage, idx) => {
              const stages = ['Uploaded', 'Processing', 'Extracting', 'Evidence Ready'];
              const currentIdx = stages.indexOf(processingStage);
              const isPast = idx <= currentIdx;

              return (
                <div key={stage} style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <div
                    style={{
                      height: 5,
                      borderRadius: 999,
                      background: isPast ? 'var(--gold-primary)' : 'rgba(255,255,255,0.1)',
                      boxShadow: isPast ? '0 0 10px rgba(245, 199, 124, 0.6)' : 'none',
                      transition: 'all 0.3s ease',
                    }}
                  />
                  <small style={{ fontSize: 10.5, color: isPast ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                    {stage}
                  </small>
                </div>
              );
            })}
          </div>
        </GlassCard>
      )}

      {/* 3. Floating Upload Action */}
      <GlassCard variant="default">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <div>
            <h3 style={{ fontSize: 16 }}>
              {language === 'hi' ? 'नया दस्तावेज़ जोड़ें' : 'Add New Document'}
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: 12.5 }}>
              Upload Aadhaar, BOCW Worker Card, or Ration Card
            </p>
          </div>
          <span style={{ fontSize: 24, color: 'var(--gold-primary)' }}>📄</span>
        </div>

        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: 1, minWidth: 260 }}>
            <GlassSelect
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              placeholder={language === 'hi' ? 'दस्तावेज़ प्रकार चुनें' : 'Select Document Type'}
              options={[
                {
                  value: 'BOCW_CARD',
                  label: language === 'hi' ? 'निर्माण श्रमिक पासबुक (BOCW Worker Passbook)' : 'BOCW Worker Passbook (निर्माण श्रमिक पासबुक)',
                },
                {
                  value: 'AADHAAR',
                  label: language === 'hi' ? 'आधार कार्ड (Aadhaar Card)' : 'Aadhaar Card (आधार कार्ड)',
                },
                {
                  value: 'RATION_CARD',
                  label: language === 'hi' ? 'राशन कार्ड (Ration Card)' : 'Ration Card (राशन कार्ड)',
                },
                {
                  value: 'GENERAL',
                  label: language === 'hi' ? 'सामान्य प्रमाण पत्र / आय प्रमाण पत्र' : 'General Proof / Income Certificate',
                },
              ]}
            />
          </div>

          <input
            ref={fileInput}
            type="file"
            accept="application/pdf,image/png,image/jpeg"
            hidden
            onChange={(e) => uploadDocument(e.target.files?.[0])}
          />

          <GlassButton
            type="button"
            variant="primary"
            size="md"
            fullWidth={false}
            disabled={!!processingStage}
            onClick={() => fileInput.current?.click()}
          >
            {processingStage ? 'Processing...' : language === 'hi' ? 'दस्तावेज़ चुनें →' : 'Upload Document →'}
          </GlassButton>
        </div>

        {uploadError && <ErrorState error={uploadError} />}
      </GlassCard>

      {/* 4. Evidence Graph Visualization (Major JanSetu Visual Feature) */}
      <EvidenceGraph />

      {/* 5. Document Cards List */}
      <section className="stack" style={{ gap: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ fontSize: 16 }}>
            {language === 'hi' ? 'सत्यापित दस्तावेज़ सूची' : 'Uploaded Evidence Records'}
          </h3>
          <StatusPill tone="blue">{docs.length} Documents</StatusPill>
        </div>

        {loading && <LoadingState />}
        {error && <ErrorState error={error} onRetry={loadDocuments} />}

        {!loading && !error && docs.length === 0 && (
          <GlassCard style={{ textAlign: 'center', padding: '36px 20px' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
              {language === 'hi'
                ? 'अभी तक कोई दस्तावेज़ अपलोड नहीं हुआ है। ऊपर से अपना पहला दस्तावेज़ जोड़ें।'
                : 'No documents uploaded yet. Upload your first document to unlock eligible schemes.'}
            </p>
          </GlassCard>
        )}

        {!loading &&
          !error &&
          docs.map((d) => (
            <DocumentCard
              key={d.id}
              document={d}
              onClick={() => navigate(`/documents/${d.id}`)}
            />
          ))}
      </section>
    </div>
  );
}

export function DocumentDetail() {
  const { id } = useParams<{ id: string }>();
  const { currentCitizenId } = useAuth();
  const [document, setDocument] = useState<DocumentDetailResponse | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (id && currentCitizenId) {
      documentApi.getDocument(currentCitizenId, id).then(setDocument).catch(setError);
    }
  }, [currentCitizenId, id]);

  if (error) return <ErrorState error={error} onRetry={() => navigate('/documents')} />;
  if (!document) return <LoadingState />;

  const isVerified = document.verification_status === 'VERIFIED';

  return (
    <div className="stack">
      <GlassCard variant="hero">
        <button
          type="button"
          onClick={() => navigate('/documents')}
          style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 12, display: 'inline-flex', alignItems: 'center', gap: 6 }}
        >
          ‹ Back to Documents
        </button>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
              <StatusPill tone="blue">{document.status}</StatusPill>
              <StatusPill tone={isVerified ? 'emerald' : 'amber'}>
                {document.verification_status}
              </StatusPill>
            </div>
            <h1 style={{ fontSize: 24 }}>{document.document_type}</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>ID: {document.id}</p>
          </div>
        </div>
      </GlassCard>

      {/* Extracted Statutory Claims */}
      <GlassCard variant="default">
        <h3 style={{ fontSize: 16, marginBottom: 12 }}>Extracted Statutory Claims</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {Object.entries(document.extracted_data).map(([field, value]) => (
            <div
              key={field}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: 12,
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)',
              }}
            >
              <span style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{field}</span>
              <strong style={{ color: 'var(--text-primary)', fontSize: 13 }}>{String(value)}</strong>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* Linked Evidence Artifacts */}
      <GlassCard variant="default">
        <h3 style={{ fontSize: 16, marginBottom: 12 }}>Linked Evidence Artifacts</h3>
        {document.evidence.map((item) => (
          <div
            key={item.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '10px 0',
              borderBottom: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ color: '#34d399', fontSize: 16 }}>✓</span>
              <div>
                <strong style={{ fontSize: 13.5, color: '#f8fafc' }}>{item.evidence_type}</strong>
                <small style={{ color: 'var(--text-muted)', display: 'block' }}>
                  Confidence: {item.confidence} • Status: {item.verification_status}
                </small>
              </div>
            </div>
            <StatusPill tone="blue" size="sm">Active</StatusPill>
          </div>
        ))}
      </GlassCard>
    </div>
  );
}
