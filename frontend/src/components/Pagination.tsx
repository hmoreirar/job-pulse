interface PaginationProps {
  page: number
  pages: number
  total: number
  onPageChange: (page: number) => void
}

function buildPages(current: number, total: number): number[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, index) => index + 1)
  }

  const pages = new Set<number>([1, total, current, current - 1, current + 1])
  return Array.from(pages)
    .filter((page) => page >= 1 && page <= total)
    .sort((a, b) => a - b)
}

export function Pagination({ page, pages, total, onPageChange }: PaginationProps) {
  if (pages <= 1) {
    return null
  }

  const pageItems = buildPages(page, pages)

  return (
    <nav className="pagination" aria-label="Paginación">
      <button
        type="button"
        className="pagination-button"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        Anterior
      </button>

      {pageItems.map((item, index) => {
        const previous = pageItems[index - 1]
        const showGap = previous !== undefined && item - previous > 1
        return (
          <span key={item} className="pagination-group">
            {showGap && <span className="pagination-ellipsis">...</span>}
            <button
              type="button"
              className={`pagination-button${item === page ? ' pagination-button-active' : ''}`}
              onClick={() => onPageChange(item)}
            >
              {item}
            </button>
          </span>
        )
      })}

      <button
        type="button"
        className="pagination-button"
        disabled={page >= pages}
        onClick={() => onPageChange(page + 1)}
      >
        Siguiente
      </button>

      <span className="pagination-total">{total} ofertas</span>
    </nav>
  )
}
