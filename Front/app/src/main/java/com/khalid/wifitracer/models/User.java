package com.khalid.wifitracer.models;

import com.google.gson.annotations.SerializedName;

public class User {
    @SerializedName("MAC")
    private String mac;



    @Override
    public String toString() {
        return "User {" +
                "MAC=" + mac +
                '}';
    }


}
