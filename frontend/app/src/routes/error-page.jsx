import { useRouteError } from "react-router-dom";

export function ErrorPage() {
  const error = useRouteError();
  console.error(error);

  return (
    <div id="error-page" className="flex flex-col items-center justify-center h-screen">
      <div className="bg-emerald-500 p-3 rounded text-lg text-slate-300">
          <h1 className="text-2xl font-semibold">Oops!</h1>
          <p>Sorry, an unexpected error has occurred.</p>
          <p>
            <i className="text-red-500">{error.statusText || error.message}</i>
          </p>
          <p>Please, try again later.</p>
      </div>
    </div>
  );
}