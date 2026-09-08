import "./pagination.css";

export function Pagination({ currentPage, numPages, onPageChange }) {
  if (numPages <= 1) return null;
  return (
    <nav className="pagination" aria-label="Pagination">
      <button
        type="button"
        className="btn-secondary"
        disabled={currentPage <= 1}
        onClick={() => onPageChange(currentPage - 1)}
      >
        Previous
      </button>
      <span className="pagination-status">Page {currentPage} of {numPages}</span>
      <button
        type="button"
        className="btn-secondary"
        disabled={currentPage >= numPages}
        onClick={() => onPageChange(currentPage + 1)}
      >
        Next
      </button>
    </nav>
  );
}
