
public class NFCReaderTest {

	public static void main(String[] args) {
		NFCReader reader = new NFCReader();
		if(!reader.initialize()) {
			System.out.println("Initialization failed");
			return;
		}
		while(true) {
			if(reader.tryReadCard()) {
				System.out.println("Read card");
				System.out.println("Serial number: " + reader.getSerialNumber());
				System.out.println("Raw data:");
				reader.dumpRawContents();
				System.out.println("Contents:");
				System.out.println(reader.getContents());
				System.out.println();
			}
			
			try {
				Thread.sleep(1000);
			} catch (InterruptedException e) {
			}
		}
	}

}
