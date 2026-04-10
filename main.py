import cv2
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Captura frames de vídeo, câmera ou RTSP.")
    parser.add_argument("source", help="Caminho do arquivo de vídeo, índice da câmera (ex: 0) ou URL RTSP")
    parser.add_argument("--type", choices=["video", "camera", "rtsp"], default=None,
                        help="Tipo da fonte (opcional, mas ajuda na interpretação).")
    parser.add_argument("--no-display", action="store_true",
                        help="Executa sem exibir a janela (modo headless). A interação por teclado é desabilitada.")
    parser.add_argument("--save-interval", type=float, default=0.0,
                        help="Intervalo em segundos para salvar frames automaticamente (ex: 1.0 para 1 frame por segundo).")
    args = parser.parse_args()

    # Determinar o tipo de fonte se não especificado
    source_type = args.type
    if source_type is None:
        if args.source.isdigit():
            source_type = "camera"
        elif args.source.startswith(("rtsp://", "http://", "https://")):
            source_type = "rtsp"
        else:
            source_type = "video"

    # Abrir a captura de acordo com o tipo
    if source_type == "camera":
        cap = cv2.VideoCapture(int(args.source))
    else:
        cap = cv2.VideoCapture(args.source)

    if not cap.isOpened():
        print("Erro: não foi possível abrir a fonte.")
        sys.exit(1)

    # Obter FPS da fonte para cálculo do intervalo de frames
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        # Valor padrão caso não seja possível obter o FPS (comum em câmeras/RTSP)
        fps = 30.0
        print("Aviso: FPS não detectado. Usando padrão de 30 FPS para salvamento automático.")

    auto_save_interval_frames = 0
    if args.save_interval > 0:
        auto_save_interval_frames = int(round(fps * args.save_interval))
        if auto_save_interval_frames < 1:
            auto_save_interval_frames = 1
        print(f"Salvamento automático ativado: 1 frame a cada {args.save_interval} segundo(s) (~{auto_save_interval_frames} frames).")
    else:
        auto_save_interval_frames = 0

    print(f"Capturando de {source_type}: {args.source}")
    if args.no_display:
        print("Modo sem exibição ativado. Processando até o fim da captura...")
    else:
        print("Pressione 'q' para sair, 's' para salvar o frame atual.")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Fim da captura ou erro ao ler frame.")
            break

        # Salvamento automático baseado no intervalo configurado
        if auto_save_interval_frames > 0 and frame_count % auto_save_interval_frames == 0:
            filename = f"frame_{frame_count:06d}.png"
            cv2.imwrite(filename, frame)
            print(f"Frame salvo automaticamente como {filename}")

        # Exibição e interação (apenas se não estiver em modo headless)
        if not args.no_display:
            cv2.imshow("Captura de Frames", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Salvamento manual (nome baseado no contador atual)
                filename = f"frame_{frame_count:06d}_manual.png"
                cv2.imwrite(filename, frame)
                print(f"Frame salvo manualmente como {filename}")

        frame_count += 1

    cap.release()
    if not args.no_display:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()