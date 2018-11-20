/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package fillstats;

import java.io.File;
import java.io.FileNotFoundException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.ParseException;
import java.util.Arrays;
import java.util.Scanner;


/**
 *
 * @author bkschwar
 */
public class FillStats {

    /**
     * @param args the command line arguments
     */
   private static DBConnect dbConnect = new DBConnect();
    
    public static void main(String[] args) throws SQLException,ParseException, FileNotFoundException{
        String[] fileNames = {"Game.csv","Player.csv","Advanced.csv","PerGame.csv","PerPos.csv","Play_By_Play.csv",
            "Playoff_Game.csv","Playoffs_Advanced.csv","Playoffs_PerGame.csv","Playoffs_PerPos.csv",
            "Playoffs_Play_By_Play.csv","Playoffs_Shooting.csv","Playoffs_Totals.csv","Shooting.csv","Totals.csv"};
        
        for (String file:fileNames)
        {
            CSVReader csvreader = new CSVReader(file);
            csvreader.getHeaders();
            csvreader.getData();
            csvreader.insertData();
        }
        
        
        //System.out.println(Arrays.toString(s.split(",")));
        //csvreader.getData();
        /*try ( // TODO code application logic here
                Connection con = dbConnect.getConnection()) {
            if (con == null) {
                throw new SQLException("Can't get database connection");
            }
            con.setAutoCommit(false);
            
            Statement statement = con.createStatement();
            
            PreparedStatement preparedStatement = con.prepareStatement("Insert into \"Player\" values(?,?,?,?)");
            preparedStatement.setInt(1, 21);
            preparedStatement.setString(2, "Brian Schwartz");
            preparedStatement.setInt(3, 145);
            preparedStatement.setInt(4, 68);
            //preparedStatement.setDate(4, new java.sql.Date(created_date.getTime()));
            preparedStatement.executeUpdate();
            statement.close();
            con.commit();
        }
        //Util.invalidateUserSession();*/
    }

    }
    
