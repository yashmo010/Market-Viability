import React from 'react';
import { SlidersHorizontal, Building2 } from 'lucide-react';

/**
 * Schema-driven category specification fields (Requirement 1).
 * Renders whatever `fields` the API's /api/spec_schema returns for the category.
 * Every field is OPTIONAL — nothing here blocks submission.
 */
export function CategorySpecFields({ categoryLabel, fields, values, onChange }) {
  if (!fields || fields.length === 0) return null;

  const renderField = (field) => {
    const val = values[field.key] ?? '';
    const common = {
      value: val,
      onChange: (e) => onChange(field.key, e.target.value),
      style: styles.input,
    };

    if (field.type === 'select' || field.type === 'boolean') {
      const options = field.type === 'boolean' ? ['Yes', 'No'] : (field.options || []);
      return (
        <select {...common} style={styles.select}>
          <option value="">—</option>
          {options.map((opt) => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      );
    }
    return (
      <input
        {...common}
        type={field.type === 'number' ? 'number' : 'text'}
        placeholder={field.placeholder || ''}
      />
    );
  };

  return (
    <div style={styles.block}>
      <div style={styles.blockHeader}>
        <SlidersHorizontal size={15} color="var(--accent)" />
        <span style={styles.blockTitle}>{categoryLabel} Specifications</span>
        <span style={styles.optionalTag}>all optional</span>
      </div>
      <div style={styles.grid}>
        {fields.map((field) => (
          <div key={field.key} style={styles.fieldGroup}>
            <label style={styles.fieldLabel}>
              {field.label}{field.unit ? ` (${field.unit})` : ''}
            </label>
            {renderField(field)}
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Company / product maturity block (Requirement 2).
 * Feeds trust & repairability adjustment logic in the model layer.
 */
export function MaturityBlock({
  companyMaturity, setCompanyMaturity,
  productMaturity, setProductMaturity,
}) {
  const isNew = companyMaturity === 'new' || productMaturity === 'new';
  return (
    <div style={styles.block}>
      <div style={styles.blockHeader}>
        <Building2 size={15} color="var(--accent)" />
        <span style={styles.blockTitle}>Company &amp; Product Maturity</span>
      </div>
      <div style={styles.grid}>
        <div style={styles.fieldGroup}>
          <label style={styles.fieldLabel}>Company</label>
          <select
            value={companyMaturity}
            onChange={(e) => setCompanyMaturity(e.target.value)}
            style={styles.select}
          >
            <option value="established">Established (has track record)</option>
            <option value="new">New / unknown brand</option>
          </select>
        </div>
        <div style={styles.fieldGroup}>
          <label style={styles.fieldLabel}>Product</label>
          <select
            value={productMaturity}
            onChange={(e) => setProductMaturity(e.target.value)}
            style={styles.select}
          >
            <option value="iterated">Existing / iterated product</option>
            <option value="new">New line / first product</option>
          </select>
        </div>
      </div>
      {isNew && (
        <p style={styles.maturityHint}>
          No market history yet — trust, after-sales and repairability will be graded
          down and confidence lowered, with a note in the results.
        </p>
      )}
    </div>
  );
}

const styles = {
  block: {
    backgroundColor: 'var(--bg-panel)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-lg)',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    boxShadow: 'var(--shadow-sm)',
  },
  blockHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  blockTitle: {
    fontSize: '14px',
    fontWeight: 600,
    color: 'var(--text-primary)',
  },
  optionalTag: {
    marginLeft: 'auto',
    fontSize: '10px',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: 'var(--text-muted)',
    backgroundColor: 'var(--bg-input)',
    border: '1px solid var(--border)',
    borderRadius: '10px',
    padding: '2px 8px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
    gap: '14px',
  },
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  fieldLabel: {
    fontSize: '12px',
    fontWeight: 500,
    color: 'var(--text-secondary)',
  },
  input: {
    height: '40px',
  },
  select: {
    height: '40px',
    cursor: 'pointer',
  },
  maturityHint: {
    fontSize: '12px',
    color: 'var(--warning)',
    lineHeight: 1.5,
    margin: 0,
  },
};
