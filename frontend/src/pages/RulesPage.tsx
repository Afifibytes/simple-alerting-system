import React, { useState } from 'react';
import { RuleForm } from '../components/rules/RuleForm';
import { RuleList } from '../components/rules/RuleList';
import { useRules } from '../hooks/useRules';
import { useSources } from '../hooks/useSources';
import { useNotifications } from '../hooks/useNotifications';
import type { RuleFormData } from '../types';

interface RulesPageProps {
  showForm: boolean;
  onFormComplete: () => void;
}

export function RulesPage({ showForm, onFormComplete }: RulesPageProps): React.ReactElement {
  const { rules, loading, createRule, updateRule, deleteRule } = useRules();
  const { sources, loading: sourcesLoading } = useSources();
  const { channels, loading: channelsLoading } = useNotifications();
  const [creating, setCreating] = useState(false);

  const handleCreateRule = async (rule: RuleFormData): Promise<void> => {
    setCreating(true);
    try {
      await createRule(rule);
      onFormComplete();
    } finally {
      setCreating(false);
    }
  };

  return (
    <>
      {showForm && (
        <>
          <RuleForm
            onSubmit={handleCreateRule}
            loading={creating}
            sources={sources}
            loadingSources={sourcesLoading}
            channels={channels}
            loadingChannels={channelsLoading}
          />
          <div className="section-divider" />
        </>
      )}
      <RuleList
        rules={rules}
        loading={loading}
        onDelete={deleteRule}
        onUpdate={updateRule}
      />
    </>
  );
}
