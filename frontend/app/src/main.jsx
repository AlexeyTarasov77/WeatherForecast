import React from 'react'
import ReactDOM from 'react-dom/client'
import {
  RouterProvider,
} from "react-router-dom";
import './index.css'

import { createBrowserRouter } from "react-router-dom";
import { Root, DailyForecast, HourlyForecast, hourlyForecastLoader, ErrorPage } from "./routes";

const router = createBrowserRouter([
    {
      path: "/",
      element: <Root />,
      errorElement: <ErrorPage />
    },
    {
      path: "/forecast/daily",
      element: <DailyForecast />,
    },
    {
      path: "/forecast/hourly/:date",
      element: <HourlyForecast />,
      loader: hourlyForecastLoader
    },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
