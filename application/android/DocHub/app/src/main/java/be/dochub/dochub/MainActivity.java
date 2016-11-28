package be.dochub.dochub;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;

public class MainActivity extends AppCompatActivity {

    private WebView mWebView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mWebView = (WebView) findViewById(R.id.activity_main_webview);

        // Stop local links and redirects from opening in browser instead of WebView
        mWebView.setWebViewClient(new DocHubWebViewClient());
        mWebView.setWebChromeClient(new DocHubWebChromeClient());

        // Enable Javascript
        WebSettings webSettings = mWebView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setAllowFileAccess(true);
        mWebView.loadUrl("https://www.ulb.ac.be/commons/intranet?_prt=ulb:gehol&_ssl=on&_prtm=redirect&_appl=http://dochub.be/auth");
    }

    @Override
    public void onBackPressed() {
        if(mWebView.canGoBack()) {
            mWebView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
