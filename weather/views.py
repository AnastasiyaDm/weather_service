from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
import requests
from rest_framework.views import APIView
from .models import Weather, Forecast, City
from .serializer import UserSerializer, GroupSerializer, WeatherSerializer, ForecastSerializer, CitySerializer

API_KEY = "6034d87efaa342b60bd74f470f24eb86"


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class WeatherDetail(APIView):

    def get(self, request, city):
        url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(city, API_KEY)

        response = requests.get(url).json()

        if response.get('cod') != 200:
            return Response(response, status=400)

        data = {
            "city": {
                "city_name": response.get("name"),
                "cord_lon": response["coord"]["lon"],
                "cord_lat": response["coord"]["lat"]
            },
            "weather_main": response["weather"][0]["main"],
            "weather_description": response["weather"][0]["description"],
            "temp": response["main"]["temp"],
            "date_time": response.get("dt")
        }

        serializer = WeatherSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)


class WeatherList(APIView):

    def get(self, request):
        weather = Weather.objects.all()
        serializer = WeatherSerializer(weather, many=True)
        return Response(serializer.data)


class ForecastList(APIView):

    def get(self, request):
        forecast = Forecast.objects.all()
        serializer = ForecastSerializer(forecast, many=True)
        return Response(serializer.data)


class ForecastDetail(APIView):

    def get(self, request, city, cnt):

        forecast_url = "http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&cnt={}&appid={}".\
            format(city, cnt, API_KEY)
        response = requests.get(forecast_url).json()

        if response.get('cod') != 200:
            return Response(response, status=400)

        weather_data = []
        res1 = {"city": {
            'city_name': response["city"]["name"],
            'cord_lon': response["city"]["coord"]["lon"],
            'cord_lat': response["city"]["coord"]["lat"]}
        }
        res2 = {}
        for i in response['list']:
            res2['weather_main'] = i['weather'][0]['main']
            res2['weather_description'] = i['weather'][0]['description']
            res2['temp'] = i['main']['temp']
            res2['date_time'] = i['dt']
            result = {**res1, **res2}
            weather_data.append(result)
        serializer = ForecastSerializer(data=weather_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)








