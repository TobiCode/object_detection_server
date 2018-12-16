package com.example.tew.test;

import android.graphics.Color;
import android.os.AsyncTask;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import java.util.HashMap;
import java.util.Timer;
import java.util.TimerTask;

public class MainActivity extends AppCompatActivity {

    TextView textView;
    Boolean warningFlag;
    Boolean ipAddressSet;
    EditText ipAddressField;
    String savedIpAddress;
    private Timer timerAsync;
    private TimerTask timerTaskAsync;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        warningFlag = false;
        textView = (TextView) findViewById(R.id.textViewId);
        ipAddressField = (EditText) findViewById(R.id.ipAddressEditText);
        ipAddressSet = false;
    }


    public void changeColorTextView() {
        if (warningFlag) {
            textView.setBackgroundColor(Color.RED);
            textView.setText("Warning");
        } else {
            textView.setBackgroundColor(Color.GREEN);
            textView.setText("No Warning");

        }
    }

    public void saveIpAddressOnClick(View view){
        savedIpAddress = ipAddressField.getText().toString();
        ipAddressSet = true;
    }

    public void syncServer(View view) {
        if(ipAddressSet){
        //new GetInfo().execute();
        startBackgroundPerform();}
        else{
            Toast.makeText(this, "Need to set the Ip Address first", Toast.LENGTH_SHORT).show();
        }
    }

    public void stopSync(View view){
        timerTaskAsync.cancel();
        timerAsync.cancel();
    }


    public void startBackgroundPerform() {
        final Handler handler = new Handler();
        timerAsync = new Timer();
        timerTaskAsync = new TimerTask() {
            @Override
            public void run() {
                handler.post(new Runnable() {
                    public void run() {
                        try {
                            GetInfo performBackgroundTask =
                                    new GetInfo();
                            performBackgroundTask.execute();
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                });
            }
        };
        timerAsync.schedule(timerTaskAsync, 0, 1000);
    }


    private class GetInfo extends AsyncTask<Void, Void, String> {

        @Override
        protected String doInBackground(Void... voids) {
            // These two need to be declared outside the try/catch
            // so that they can be closed in the finally block.
            HttpURLConnection urlConnection = null;
            BufferedReader reader = null;

            // Will contain the raw JSON response as a string.
            String infoWarningString = null;

            try {
                URL url = new URL("http://" + savedIpAddress + ":8010");

                // Create the request to OpenWeatherMap, and open the connection
                urlConnection = (HttpURLConnection) url.openConnection();
                urlConnection.setRequestMethod("GET");
                urlConnection.connect();

                // Read the input stream into a String
                InputStream inputStream = urlConnection.getInputStream();
                StringBuffer buffer = new StringBuffer();
                if (inputStream == null) {
                    // Nothing to do.
                    return null;
                }
                reader = new BufferedReader(new InputStreamReader(inputStream));

                String line;
                while ((line = reader.readLine()) != null) {
                    // Since it's JSON, adding a newline isn't necessary (it won't affect parsing)
                    // But it does make debugging a *lot* easier if you print out the completed
                    // buffer for debugging.
                    buffer.append(line);
                }

                if (buffer.length() == 0) {
                    // Stream was empty.  No point in parsing.
                    return null;
                }
                infoWarningString = buffer.toString();
                Log.i("DebugTest1:", infoWarningString);
                return infoWarningString;

            } catch (Exception e) {
                Toast.makeText(MainActivity.this, e.toString(), Toast.LENGTH_SHORT).show();
                return null;

            } finally {
                if (urlConnection != null) {
                    urlConnection.disconnect();
                }
                if (reader != null) {
                    try {
                        reader.close();
                    } catch (final IOException e) {
                        Log.i("PlaceholderFragment", "Error closing stream", e);
                    }
                }
            }
        }

        @Override
        protected void onPostExecute(String s) {
            super.onPostExecute(s);
            Log.i("DebugTest2:", s);
            JSONObject fieldsJson = null;
            try {
                fieldsJson = new JSONObject(s);
                String value = fieldsJson.getString("warning");
                warningFlag = Boolean.parseBoolean(value);

            } catch (JSONException e) {
                e.printStackTrace();
            }
            changeColorTextView();
        }

    }

}

