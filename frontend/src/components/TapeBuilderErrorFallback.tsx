import { Link } from "react-router-dom";
import { AxiosError } from "axios";

interface TapeBuilderErrorFallbackProps {
  error: unknown;
}

function TapeBuilderErrorFallback({ error }: TapeBuilderErrorFallbackProps) {
  const isNotFound =
    error instanceof AxiosError && error.response?.status === 404;

  const isForbidden =
    error instanceof AxiosError && error.response?.status === 403;

  const title = isNotFound
    ? "Tape not found"
    : isForbidden
      ? "Access denied"
      : "Something went wrong";

  const message = isNotFound
    ? "This tape doesn't exist or you don't have access to it."
    : isForbidden
      ? "You don't have access to this tape."
      : "There was a problem loading this tape. Please try again.";

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <h1 className="text-xl font-bold">{title}</h1>
      <p className="text-sm text-gray-500">{message}</p>
      <Link
        to="/"
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Back to home
      </Link>
    </div>
  );
}

export default TapeBuilderErrorFallback;