/**
 * 
 * @author Logan
 * Sends out keyboard commands to type out the contents of the NFC tag
 */
import java.awt.AWTException;
import java.awt.Robot;
import java.awt.event.KeyEvent;

public class NFCReaderTyper {
	static final int WAIT_TIME = 250; 
	static final int DONE_WAIT_TIME = 2000;
	
	public static void main(String[] args) {
		NFCReader reader = new NFCReader();
		Robot robot = null;
		try {
			robot = new Robot();
		} catch (AWTException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
			System.out.println("Failed to initialize Robot");
			return;
		}
		if(!reader.initialize()) {
			System.out.println("Reader failed to initialize");
			return;
		}
		while(true) {
			if(reader.tryReadCard()) {
				String contents = reader.getContents();
				//type out contents
				boolean first = true;
				char lastChar = 0;
				for(char c : contents.toCharArray()) {
					if(c >= '0' && c <= '9') {
						robot.keyPress(c);
						robot.delay(10);
						robot.keyRelease(c);
					}
					else if(c >= 'A' && c <= 'Z') {
						robot.keyPress(KeyEvent.VK_SHIFT);
						robot.keyPress(c);
						robot.keyRelease(KeyEvent.VK_SHIFT);
						robot.delay(10);
						robot.keyRelease(c);
					}
					else if(c >= 'a' && c <= 'z') {
						robot.keyPress(Character.toUpperCase(c));
						robot.delay(10);
						robot.keyRelease(Character.toUpperCase(c));
					}
					
					lastChar = c;
				}
				robot.keyRelease(Character.toUpperCase(lastChar));
				robot.delay(100);
				robot.keyPress(KeyEvent.VK_ENTER);
				robot.keyRelease(KeyEvent.VK_ENTER);
				
				try {
					Thread.sleep(DONE_WAIT_TIME);
				} catch (InterruptedException e) {
				}
			}
			
			try {
				Thread.sleep(WAIT_TIME);
			} catch (InterruptedException e) {
			}
		}
	}

}
