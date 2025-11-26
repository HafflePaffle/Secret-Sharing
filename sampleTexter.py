import argparse
from pathlib import Path

def pdf_to_bytes_txt(pdf_path: Path, out_path: Path, fmt: str = 'dec', chunk_size: int = 65536):
    pdf_path = Path(pdf_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fmt = fmt.lower()
    if fmt not in ('dec', 'hex', 'line'):
        raise ValueError("fmt must be one of: 'dec', 'hex', 'line'")

    total = 0
    with pdf_path.open('rb') as fin, out_path.open('w', encoding='utf-8') as fout:
        while True:
            chunk = fin.read(chunk_size)
            if not chunk:
                break
            total += len(chunk)
            if fmt == 'dec':
                fout.write(' '.join(str(b) for b in chunk) + ' ')
            elif fmt == 'hex':
                fout.write(' '.join(f'{b:02x}' for b in chunk) + ' ')
            else:  # line: one byte per line (decimal)
                fout.write('\n'.join(str(b) for b in chunk) + '\n')
    return total

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read a PDF and write its raw bytes into a text file.')
    parser.add_argument('pdf', nargs='?', default='Hafsteinn Petursson - Dilemmas Exam.pdf', help='Input PDF file path (default: input.pdf)')
    parser.add_argument('-o', '--out', default='pdf_bytes.txt', help='Output text file (default: pdf_bytes.txt)')
    parser.add_argument('--format', choices=['dec', 'hex', 'line'], default='dec',
                        help="Output format: 'dec' (space-separated decimals), 'hex' (space-separated hex), 'line' (one decimal per line)")
    parser.add_argument('--chunk', type=int, default=65536, help='Read chunk size in bytes (default 65536)')
    args = parser.parse_args()

    written = pdf_to_bytes_txt(args.pdf, args.out, fmt=args.format, chunk_size=args.chunk)
    print(f'Wrote {written} bytes from "{args.pdf}" into "{args.out}" as format {args.format}')