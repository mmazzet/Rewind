function AppErrorFallback() {
  function handleReload() {
    window.location.reload();
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <h1 className="text-xl font-bold">Something went wrong</h1>
      <p className="text-sm text-gray-500">Please try reloading the page.</p>
      <button
        onClick={handleReload}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Reload page
      </button>
    </div>
  );
}

export default AppErrorFallback;
