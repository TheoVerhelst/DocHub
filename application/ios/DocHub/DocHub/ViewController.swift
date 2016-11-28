//
//  ViewController.swift
//  DocHub
//
//  Created by George Rusu on 28/11/2016.
//  Copyright © 2016 George Rusu. All rights reserved.
//

import UIKit

class ViewController: UIViewController,UIWebViewDelegate {

    
    @IBOutlet weak var WebView: UIWebView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        let webUrl : NSURL = NSURL(string: "https://dochub.be")!
        let webRequest : NSURLRequest = NSURLRequest(url: webUrl as URL)
        WebView.loadRequest(webRequest as URLRequest)        // Do any additional setup after loading the view, typically from a nib.
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}

