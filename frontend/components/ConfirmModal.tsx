interface Props {
  title: string;
  body: React.ReactNode;
  confirmLabel?: string;
  onCancel: () => void;
  onConfirm: () => void;
  isBusy: boolean;
}

export function ConfirmModal({
  title,
  body,
  confirmLabel = "Delete",
  onCancel,
  onConfirm,
  isBusy,
}: Props) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-40 px-4">
      <div className="bg-card rounded-lg max-w-md w-full p-6">
        <h2 className="text-lg font-semibold text-navy mb-3">{title}</h2>
        <div className="text-sm text-unpublished mb-6">{body}</div>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm rounded-md border border-border text-navy hover:bg-page transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isBusy}
            className="px-4 py-2 text-sm rounded-md bg-accent hover:bg-accent-hover text-white transition-colors disabled:opacity-60"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
