import { useEffect, useState } from 'react';
import { Layout } from './components/layout'
import { UiFieldInput, UiModal, UiButton, WeatherItem } from './components'
import axios from 'axios'


export default function App() {
  console.log('rerender');
  
  const serverURL = 'http://localhost:8000'
  const [weatherData, setWeatherData] = useState(null);
  const [error, setError] = useState(null);
  const [lastViewedCity, setLastViewedCity] = useState(null);

  const getLastViewedCity = async () => {
    await axios.get(serverURL + '/forecast/last-viewed-city/', {withCredentials: true})
    .then((resp) => {
      console.log(resp.data); 
      setLastViewedCity(resp.data.last_viewed_city);
      setError(null);
    })
    .catch((err) => {
      if (err.response.status === 404 && "last_viewed_city" in err.response.data) {
        setLastViewedCity(null);
        return
      }
      console.error(err);
      setError('Something went wrong, try again later');
      setWeatherData(null);
    });
  }

  const getForecastByCity = async (cityName) => {
    await axios.get(serverURL + '/forecast/', { params: { city_name: cityName }, withCredentials: true })
    .then((resp) => {
      console.log(resp.data); 
      resp.data.city = cityName
      setWeatherData(resp.data)
      setError(null);
    })
    .catch((err) => {
      console.error(err);
      setError('Error fetching weather data, try again later');
      setWeatherData(null);
    });
  }

  const handleFormSubmit = async (e) => {
    e.preventDefault()
    const data = new FormData(e.target)
    const cityName = data.get('city_name')
    if (cityName && cityName != weatherData?.city) {
      await getForecastByCity(cityName)
    }
  }

  const formatWeatherData = (data) => {
    const formattedData = [];
    const dates = data.daily.date;
    const temperatureMins = data.daily.temperature_2m_min;
    const temperatureMaxs = data.daily.temperature_2m_max;
    const rainSums = data.daily.rain_sum;

    for (let i = 0; i < Object.keys(dates).length; i++) {
      formattedData.push({
        date: new Date(dates[i]),
        temperatureMin: temperatureMins[i],
        temperatureMax: temperatureMaxs[i],
        rainSum: rainSums[i],
      });
    }

    return formattedData;
  };

  const form = (
    <form onSubmit={handleFormSubmit} className='flex flex-col items-center'>
      <UiFieldInput
        className={"mb-4"}
        placeholder="Ваш город"
        id="city"
        name="city_name"
        required
      />
      <UiButton variant="primary" size="lg" disabled={Boolean(error)}>
        Отправить
      </UiButton>
    </form>
  )
  
  const modal = (
    <UiModal
      isOpen={Boolean(lastViewedCity)}
      onClose={() => setLastViewedCity(null)}
    >
      <UiModal.Header>Хотите узнать погоду в недавно просмотренном городе {lastViewedCity}?</UiModal.Header>
      <UiModal.Footer>
        <UiButton variant='outline' onClick={() => setLastViewedCity(null)}>Нет</UiButton>
        <UiButton variant="primary" onClick={
          async () => {
            setLastViewedCity(null)
            await getForecastByCity(lastViewedCity)
          }}
        >
          Да
        </UiButton>
      </UiModal.Footer>
    </UiModal>
  )

  // useEffect(() => {
  //   console.log('lastViewedCity', lastViewedCity);
    
  //   if (!lastViewedCity) {
  //     (async () => await getLastViewedCity())()
  //   }
  // }, [lastViewedCity]);
  useEffect(() => {
    (async () => await getLastViewedCity())()
  }, [])

  return (
    <>
      <Layout form={form} modal={modal}>
      {error && <p className="text-red-500 text-2xl mt-3">{error}</p>}
      {weatherData && (
        <div className='my-5'>
          <h3 className="text-2xl mb-3">Прогноз погоды в городе {weatherData.city} на ближайшее время.</h3>
          <div className="weather-container flex gap-3 flex-wrap justify-center">
            {formatWeatherData(weatherData).map((item, index) => (
              <WeatherItem key={index} forecastItem={item}/>
            ))}
          </div>
        </div>
      )}
      </Layout>
    </>
  )
}
