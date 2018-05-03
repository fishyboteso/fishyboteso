package in.definex.fishy;

import android.app.Application;
import android.app.IntentService;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.TaskStackBuilder;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.support.annotation.RequiresApi;
import android.support.v7.app.NotificationCompat;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.DataInput;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.nio.charset.StandardCharsets;

/**
 * Created by adam_ on 13-07-2017.
 */

public class NetworkService extends IntentService {

    private int port = 8023;
    String ip;

    /**
     * A constructor is required, and must call the super IntentService(String)
     * constructor with a name for the worker thread.
     */
    public NetworkService() {
        super("NetworkService");

    }

    Handler handler;

    String jsonString;
    Context context;
    JSONObject jsonObject;
    ServerSocket serverSocket = null;
    Socket server = null;

    boolean serviceIsOn;

    @RequiresApi(api = Build.VERSION_CODES.KITKAT)
    @Override
    protected void onHandleIntent(Intent intent) {

        context = this;
        ip = intent.getStringExtra("ip");
        handler = new Handler(Looper.getMainLooper());
        BufferedReader in = null;
        try {
            serverSocket = new ServerSocket(port);
            serverSocket.setSoTimeout(10000);
        } catch (IOException e) {
            e.printStackTrace();
        }

        serviceIsOn = true;

        while(serviceIsOn){
            try{
                server = serverSocket.accept();
                in = new BufferedReader(new InputStreamReader(server.getInputStream(), "UTF-8"));

                jsonString = "";
                String line;
                while ((line = in.readLine()) != null) {
                    jsonString+=line;
                }

                System.out.println("RECEIVED: " + jsonString);

                jsonObject = new JSONObject(jsonString);

                String action = jsonObject.getString("action");

                switch (action){
                    case "holeDeplete":
                        String message = "Hole has been depleted!";
                        String subMessage = jsonObject.getInt("fishCount") + " Fishes Caught";
                        toast(message, subMessage);
                        break;
                }

                System.out.println("yoooooo");


                server.close();
            } catch (SocketException e){
                System.out.println(e);
            } catch (IOException | JSONException e) {
                System.out.println(e);
            }
        }
    }

    @Override
    public void onDestroy() {

        try {
            serviceIsOn = false;
            serverSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        toast("Service turned off","");

        super.onDestroy();
    }

    private void toast(final String message, final String subMessage){
        int notifMode = getSharedPreferences("config", Context.MODE_PRIVATE).getInt("notifMode",0);

        switch (notifMode){
            case 0:
                int mNotificationId = 8023;
                NotificationCompat.Builder mBuilder =
                        (NotificationCompat.Builder) new NotificationCompat.Builder(this)
                                .setSmallIcon(R.mipmap.ic_launcher)
                                .setContentTitle(message)
                                .setContentText(subMessage)
                                .setDefaults(Notification.DEFAULT_ALL)
                                .setPriority(Notification.PRIORITY_MAX);

                Intent resultIntent = new Intent(this, MainActivity.class);

                TaskStackBuilder stackBuilder = TaskStackBuilder.create(this);
                stackBuilder.addParentStack(MainActivity.class);
                stackBuilder.addNextIntent(resultIntent);
                PendingIntent resultPendingIntent =
                        stackBuilder.getPendingIntent(
                                0,
                                PendingIntent.FLAG_UPDATE_CURRENT
                        );

                mBuilder.setContentIntent(resultPendingIntent);

                NotificationManager mNotificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
                mNotificationManager.notify(mNotificationId, mBuilder.build());
                break;

            case 1:
                handler.post(new Runnable() {
                    @Override
                    public void run() {

                        String m = subMessage.isEmpty()?message:message+" ("+subMessage+")";

                        Toast.makeText(getApplicationContext(),
                                m,
                                Toast.LENGTH_SHORT).show();
                    }
                });
                break;

        }
    }
}