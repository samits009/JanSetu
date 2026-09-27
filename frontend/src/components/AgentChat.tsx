import React, { useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { AgentActivity } from './common/AgentActivity';
import { ConsentDialog } from './ConsentDialog';
import { GlassCard } from './common/GlassCard';
import { agentApi } from '../services/agentApi';
import { ConsentRequestData } from '../domain/models';

export function AgentChat() {
  const { currentCitizenId } = useAuth();
  const [pendingConsent, setPendingConsent] = useState<ConsentRequestData | null>(null);
  const [consentSuccess, setConsentSuccess] = useState(false);

  const handleGrantConsent = async () => {
    if (!pendingConsent) return;
    try {
      await agentApi.grantConsent(pendingConsent.id, 'GRANT', pendingConsent.application_id);
      setConsentSuccess(true);
      setPendingConsent(null);
      setTimeout(() => setConsentSuccess(false), 5000);
    } catch (err) {
      console.error('Consent authorization failed', err);
    }
  };

  const handleDenyConsent = () => {
    setPendingConsent(null);
  };

  return (
    <div className="stack" style={{ gap: 16 }}>
      {/* Consent Authorization Dialog if requested by Agent */}
      {pendingConsent && (
        <ConsentDialog
          consentRequest={pendingConsent}
          onGrant={handleGrantConsent}
          onDeny={handleDenyConsent}
        />
      )}

      {/* Success Notification if Consent Granted */}
      {consentSuccess && (
        <GlassCard variant="luminous" style={{ padding: '14px 18px', borderLeft: '4px solid #10b981' }}>
          <strong style={{ color: '#34d399', display: 'block', fontSize: 14 }}>
            ✓ Sovereign Consent Cryptographically Granted
          </strong>
          <small style={{ color: 'var(--text-secondary)', fontSize: 12.5 }}>
            JanSetu has authorized handoff of verified dossier to the official government benefits repository.
          </small>
        </GlassCard>
      )}

      {/* Core Sovereign Agent Activity Panel */}
      <AgentActivity
        citizenId={currentCitizenId}
        onConsentRequest={(data) => setPendingConsent(data)}
      />
    </div>
  );
}
