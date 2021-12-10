**Real-Time PPP 101**

Experiments in Real-Time Precise Point Positioning (PPP) with [rtklib](http://www.rtklib.com/); binaries can be accessed [here](https://github.com/tomojitakasu/RTKLIB/releases).  

For now (2021) [ephemeris and correction streams](http://products.igs-ip.net/) are focused on BNC, DLR and GMV. That is:
 - BCEP00BKG0 and SSRA02IGS0 / SSRA03IGS0 -> [BNC](https://igs.bkg.bund.de/ntrip/download) ---*this is a combination product*
 - BCEP00BKG0 and SSRA00BKG0 -> [BKG by RETICLE by GSOC/DLR](https://www.dlr.de/DE/Home/home_node.html)
 - BCEP00DLR0 and SSRA00DLR0 -> [GSOC/DLR](https://www.dlr.de/DE/Home/home_node.html)
 - BCEP00GMV0 and SSRA00GMV0 -> [magicGNSS by GMV](https://magicgnss.gmv.com/)
