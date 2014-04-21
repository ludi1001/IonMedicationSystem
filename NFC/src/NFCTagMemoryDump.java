import java.util.List;

import javax.smartcardio.Card;
import javax.smartcardio.CardChannel;
import javax.smartcardio.CardException;
import javax.smartcardio.CardTerminal;
import javax.smartcardio.CommandAPDU;
import javax.smartcardio.ResponseAPDU;
import javax.smartcardio.TerminalFactory;

/**
 * 
 * @author Logan
 * Dumps out the memory contents of circular tags from whiztags.com
 * 
 * We use RFU (reserved for future use, yes, I know, cheating (check ISO-7816-4 for the correct ones)) CLA to fetch contents.
 * Specifically, the command APDU format is:
 * 0x30 offset 0x00 0x00
 * where offset is the word offset (word = 4 bytes here).
 * e.g. 0x30 0x4 0x00 0x00 gives 16 bytes stored from address 0x4 of the tag.
 * 
 * Other useful things:
 * -The first 8 bytes will give the serial number (disregarding the 4th byte).
 * -0xFE marks the end of the memory contents (note that there might be more data afterwards
 *  because previous data was overwritten and the overwrite process does not clear out all the memory (must do a reset to do so).
 * -The 23rd byte gives the number of bytes of data
 * -0x30, 0x70, 0x71, 0x72, 0x73 all seem to do the same thing as the first byte
 * -The last two bytes of the command seem unimportant
 * 
 * -ISO-14443 governs the tag
 * -ISO-7816 governs the protocol (APDU, etc)
 */
public class NFCTagMemoryDump {
	public static void main(String[] args) throws CardException {
        TerminalFactory factory = TerminalFactory.getDefault();
        List<CardTerminal> terminals = factory.terminals().list();
        System.out.println("Terminals: " + terminals);
        // get the first terminal
        CardTerminal terminal = terminals.get(0);
        // establish a connection with the card
        Card card = terminal.connect("*");
        System.out.println("card: " + card);
        CardChannel channel = card.getBasicChannel();
        byte[]command = new byte[4];
        command[0] = 0x30;
        for(int offset = 0; offset <= 41; offset += 4) { //read every 16 bytes (4 words)
        	command[1] = (byte)offset;
        	ResponseAPDU r = channel.transmit(new CommandAPDU(command));
        	for(byte b : r.getBytes()) {
        		System.out.print(Integer.toHexString(((int)b) & 0xFF) + " ");
        		//System.out.print((char)b);
        	}
        }
	}

}
