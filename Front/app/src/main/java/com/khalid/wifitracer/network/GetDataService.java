package com.khalid.wifitracer.network;

import com.khalid.wifitracer.models.CurrentObservation;
import com.khalid.wifitracer.models.User;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Url;

public interface GetDataService {

    @GET()
    Call<CurrentObservation> covidPos(@Url String url);

    @GET()
    Call<CurrentObservation> warning(@Url String url);

}
