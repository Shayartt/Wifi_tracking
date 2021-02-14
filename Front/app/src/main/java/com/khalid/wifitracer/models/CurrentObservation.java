package com.khalid.wifitracer.models;

import com.google.gson.annotations.Expose;
import com.google.gson.annotations.SerializedName;

import java.util.List;

public class CurrentObservation {
    @SerializedName("data")
    @Expose
    private String message;

    public String getMessage() {
        return message;
    }

    public void setMessage(String m) {
        this.message = m;
    }

}
