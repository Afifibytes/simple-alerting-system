import React, { useState } from 'react';
import { SourceForm } from '../components/sources/SourceForm';
import { SourceList } from '../components/sources/SourceList';
import { useSources } from '../hooks/useSources';

interface SourcesPageProps {
  showForm: boolean;
  onFormComplete: () => void;
}

export function SourcesPage({ showForm, onFormComplete }: SourcesPageProps): React.ReactElement {
  const { sources, loading, createSource, updateSource, deleteSource } = useSources();
  const [creating, setCreating] = useState(false);

  const handleCreateSource = async (source: { name: string; description: string | null; owner: string | null }): Promise<void> => {
    setCreating(true);
    try {
      await createSource(source);
      onFormComplete();
    } finally {
      setCreating(false);
    }
  };

  return (
    <>
      {showForm && (
        <>
          <SourceForm onSubmit={handleCreateSource} loading={creating} />
          <div className="section-divider" />
        </>
      )}
      <SourceList
        sources={sources}
        loading={loading}
        onUpdate={updateSource}
        onDelete={deleteSource}
      />
    </>
  );
}
