package in.definex.fishy;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.wifi.WifiManager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.format.Formatter;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import org.w3c.dom.Text;

public class MainActivity extends AppCompatActivity {

    SharedPreferences sharedPreferences = null;
    int notifMode;

    @SuppressWarnings("deprecation")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        final Context context = this;

        sharedPreferences = getSharedPreferences("config",Context.MODE_PRIVATE);

        notifMode = sharedPreferences.getInt("notifMode",0);

        final Button notifButton = (Button)findViewById(R.id.notifMode);

        changeButtonText(notifMode, notifButton);
        notifButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                notifMode = notifMode == 0?1:0;
                sharedPreferences.edit().putInt("notifMode",notifMode).apply();
                changeButtonText(notifMode, notifButton);
            }
        });

        final Button button = (Button)findViewById(R.id.button);
        //final EditText editText = (EditText)findViewById(R.id.ipAddress);

        WifiManager wm = (WifiManager) getSystemService(WIFI_SERVICE);
        final String ip = Formatter.formatIpAddress(wm.getConnectionInfo().getIpAddress());
        ((TextView)findViewById(R.id.ipAddress)).setText("IP: "+ip);

        //startService(new Intent(context, NetworkService.class));
        button.setOnClickListener(new View.OnClickListener() {
            boolean serviceOn = false;
            @Override
            public void onClick(View view) {

                if(!serviceOn){
                    button.setText("Stop Service");
                    startService(new Intent(context, NetworkService.class));
                    serviceOn = true;
                }else{
                    button.setText("Start Service");
                    stopService(new Intent(context, NetworkService.class));
                    serviceOn = false;
                }

            }
        });

    }


    private void changeButtonText(int notifMode, Button button){
        switch (notifMode){
            case 0:
                button.setText("Notification Mode");
                break;

            case 1:
                button.setText("Toast Mode");
                break;
        }
    }
}
