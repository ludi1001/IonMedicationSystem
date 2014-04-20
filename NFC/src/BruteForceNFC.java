import java.util.List;

import javax.smartcardio.*;
/**
 * 
 * @author Logan
 * I used this to brute force the command APDU that would give the right response.
 */
public class BruteForceNFC {
	public static void main(String[] args) throws CardException  {
		System.out.println(Integer.toHexString(-1));
		
		 // show the list of available terminals
        TerminalFactory factory = TerminalFactory.getDefault();
        List<CardTerminal> terminals = factory.terminals().list();
       // System.out.println("Terminals: " + terminals);
        // get the first terminal
        CardTerminal terminal = terminals.get(0);
        // establish a connection with the card
        Card card = terminal.connect("*");
       // System.out.println("card: " + card);
        CardChannel channel = card.getBasicChannel();
       // byte[]c1 = {0x00, (byte) 0x04, 0x00, 0x00};
        int i = 0;
        do {
	        try {
	        ResponseAPDU r = channel.transmit(new CommandAPDU(convertToByteArray(i)));
	        System.out.println(toString(convertToByteArray(i)) + " " + "response: " + toString(r.getBytes()));
	        } catch(IllegalArgumentException e) {
	        	
	        }
	        ++i;
	        if(i % 1000 == 0) System.out.println(i);
        } while(i != 0);
        // disconnect
        card.disconnect(false);
	}
	public static byte[] convertToByteArray(int n) {
		byte[] arr = new byte[4];
		arr[3] = (byte) ((n & 0xFF000000) >>> 24);
		arr[2] = (byte) ((n & 0x00FF0000) >>> 16);
		arr[1] = (byte) ((n & 0x0000FF00) >>> 8);
		arr[0] = (byte) ((n & 0x000000FF));
		return arr;
	}
	public static String toString(byte[]arr) {
		String str = "";
		for(int i = 0; i < arr.length; ++i) {
			str += Integer.toHexString(((int)arr[i]) & 0xFF);
			str += " ";
		}
		return str;
	}
}

