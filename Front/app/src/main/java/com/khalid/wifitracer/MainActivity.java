package com.khalid.wifitracer;

import androidx.appcompat.app.AppCompatActivity;

import android.app.ProgressDialog;
import android.content.Context;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.app.ProgressDialog;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.khalid.wifitracer.models.CurrentObservation;
import com.khalid.wifitracer.models.User;
import com.khalid.wifitracer.network.GetDataService;
import com.khalid.wifitracer.network.RetroClientInstance;

import java.util.List;
import java.util.concurrent.TimeUnit;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "MyActivity";
    ProgressDialog progressDialog;
    String address;
    GetDataService service = RetroClientInstance.getRetrofitInstance().create(GetDataService.class);
    private Button checkButton;
    private Button covidPosB;
    private Button covidNotB;
    private TextView stateText;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        checkButton = findViewById(R.id.checkContactB);
        covidPosB = findViewById(R.id.covidPos);
        covidNotB = findViewById(R.id.notCovid);
        stateText = findViewById(R.id.state);

        progressDialog = new ProgressDialog(MainActivity.this);
        progressDialog.setMessage("Loading....");
        progressDialog.show();

        WifiManager manager = (WifiManager) getApplicationContext().getSystemService(Context.WIFI_SERVICE);
        WifiInfo info = manager.getConnectionInfo();
        address = info.getMacAddress();

        covidNotB.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                covidNegative();
            }
        });

        checkButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                checkContact();
            }
        });

        covidPosB.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                covidPos();
            }
        });


        new AsyncTaskRunner().execute("", "", "");
    }

    public void checkContact() {
            Call<CurrentObservation> call = service.warning("warning/" + address);
            call.enqueue(new Callback<CurrentObservation>() {

                @Override
                public void onResponse(Call<CurrentObservation> call, Response<CurrentObservation> response) {
                    progressDialog.dismiss();
                    System.out.println(response);
                    CurrentObservation resp = response.body();
                    System.out.println(resp.getMessage());
                    if(resp.getMessage() == "false"){
                        stateText.setText("Covid : Negative");
                        Toast.makeText(MainActivity.this, "You're safe the last 5 days!", Toast.LENGTH_SHORT).show();
                    }else if(resp.getMessage() == "true"){
                        stateText.setText("Covid : Positive");
                        Toast.makeText(MainActivity.this, "Be carefull you were near to someone who tested positive stay quarantine !", Toast.LENGTH_LONG).show();
                    }else{
                        stateText.setText("Covid : Positive");
                    }
                }

                @Override
                public void onFailure(Call<CurrentObservation> call, Throwable t) {
                    progressDialog.dismiss();
                    Toast.makeText(MainActivity.this, "Something went wrong...Please try later!", Toast.LENGTH_SHORT).show();
                    System.out.println(t.getStackTrace());
                }
            });
    }

    public void covidPos(){
        Call<CurrentObservation> call = service.covidPos("covid/" + address);
        call.enqueue(new Callback<CurrentObservation>() {

            @Override
            public void onResponse(Call<CurrentObservation> call, Response<CurrentObservation> response) {
                progressDialog.dismiss();
                System.out.println(response);
                CurrentObservation resp = response.body();
                System.out.println(resp.getMessage());
                if(resp.getMessage() == "false"){
                    Toast.makeText(MainActivity.this, "Error.......", Toast.LENGTH_SHORT).show();
                }else{
                    stateText.setText("Covid : Positive");
                    Toast.makeText(MainActivity.this, "Be carefull you  tested positive stay quarantine !", Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<CurrentObservation> call, Throwable t) {
                progressDialog.dismiss();
                Toast.makeText(MainActivity.this, "Something went wrong...Please try later!", Toast.LENGTH_SHORT).show();
            }
        });
    }

    public void covidNegative(){
        Call<CurrentObservation> call = service.covidPos("covid-neg/" + address);
        call.enqueue(new Callback<CurrentObservation>() {

            @Override
            public void onResponse(Call<CurrentObservation> call, Response<CurrentObservation> response) {
                progressDialog.dismiss();
                System.out.println(response);
                CurrentObservation resp = response.body();
                System.out.println(resp.getMessage());
                if(resp.getMessage() == "false"){
                    Toast.makeText(MainActivity.this, "Error.......", Toast.LENGTH_SHORT).show();
                }else{
                    stateText.setText("Covid : Negative");
                    Toast.makeText(MainActivity.this, "Thank you for your quarantine !", Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<CurrentObservation> call, Throwable t) {
                progressDialog.dismiss();
                Toast.makeText(MainActivity.this, "Something went wrong...Please try later!", Toast.LENGTH_SHORT).show();
            }
        });
    }
    private class AsyncTaskRunner extends AsyncTask<String, String, String> {
        @Override  protected void onPreExecute() {
            progressDialog.show();
        }
        @Override  protected String doInBackground(String... params) {
            while (true) {
                checkContact();
                try {
                    TimeUnit.SECONDS.sleep(5);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                    break;
                }
            }
            return "";
        }
        @Override   protected void onPostExecute(String result) {

        }
        @Override  protected void onProgressUpdate(String... text) {
        }
    }
}