export default function PolaroidImage({
  src,
  alt,
}: {
  src: string;
  alt: string;
}) {
  return (
    <div className="polaroid">
      <img src={src} alt={alt} />
      <span>Today’s class, less admin.</span>
    </div>
  );
}
