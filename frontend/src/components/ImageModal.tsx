interface ImageModalProps {
  imageUrl: string;
  onClose: () => void;
}

export const ImageModal = ({ imageUrl, onClose }: ImageModalProps) => {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content">
        <img src={imageUrl} alt="Enlarged book cover" onClick={(e) => e.stopPropagation()} />
        <button className="modal-close-btn" onClick={onClose}>&times;</button>
      </div>
    </div>
  );
};