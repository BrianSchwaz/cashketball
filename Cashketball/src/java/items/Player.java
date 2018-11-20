/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package items;
/**
 *
 * @author macbookpro
 */
import java.io.Serializable;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.List;
import javax.annotation.ManagedBean;
import javax.faces.application.FacesMessage;
import javax.faces.bean.SessionScoped;
import javax.faces.component.UIComponent;
import javax.faces.context.FacesContext;
import javax.faces.validator.ValidatorException;
import javax.inject.Named;
import java.util.Date;
import java.util.TimeZone;

@Named(value = "Player")
@SessionScoped
@ManagedBean
public class Player implements Serializable {

    private DBConnect dbConnect = new DBConnect();
    private Integer pid;
    private String name;
    private Integer height;
    private Integer weight;
    private Date created_date;


    public Integer getPlayerID() throws SQLException {
        if (pid == null) {
            Connection con = dbConnect.getConnection();

            if (con == null) {
                throw new SQLException("Can't get database connection");
            }

            PreparedStatement ps
                    = con.prepareStatement(
                            "select max(Player_id)+1 from Player");
            ResultSet result = ps.executeQuery();
            if (!result.next()) {
                return null;
            }
            pid = result.getInt(1);
            result.close();
            con.close();
        }
        return pid;
    }

    public void setPlayerID(Integer PlayerID) {
        this.pid = PlayerID;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getWeight() {
        return weight;
    }

    public void setWeight(Integer weight) {
        this.weight = weight;
    }

    public Date getCreated_date() {
        return created_date;
    }

    public void setCreated_date(Date created_date) {
        TimeZone.setDefault(TimeZone.getTimeZone("GMT"));
        this.created_date = created_date;
    }

    public String createPlayer() throws SQLException, ParseException {
        Connection con = dbConnect.getConnection();

        if (con == null) {
            throw new SQLException("Can't get database connection");
        }
        con.setAutoCommit(false);

        Statement statement = con.createStatement();

        PreparedStatement preparedStatement = con.prepareStatement("Insert into 'Player' values(?,?,?,?)");
        preparedStatement.setInt(1, pid);
        preparedStatement.setString(2, name);
        preparedStatement.setInt(3, weight);
        preparedStatement.setInt(4, height);
        preparedStatement.setDate(4, new java.sql.Date(created_date.getTime()));
        preparedStatement.executeUpdate();
        statement.close();
        con.commit();
        con.close();
        Util.invalidateUserSession();
        return "main";
    }

    public String deletePlayer() throws SQLException, ParseException {
        Connection con = dbConnect.getConnection();

        if (con == null) {
            throw new SQLException("Can't get database connection");
        }
        con.setAutoCommit(false);

        Statement statement = con.createStatement();
        statement.executeUpdate("Delete from Player where Player_id = " + pid);
        statement.close();
        con.commit();
        con.close();
        Util.invalidateUserSession();
        return "main";
    }

    public String showPlayer() {
        return "showPlayer";
    }

    public Player getPlayer() throws SQLException {
        Connection con = dbConnect.getConnection();

        if (con == null) {
            throw new SQLException("Can't get database connection");
        }

        PreparedStatement ps
                = con.prepareStatement(
                        "select * from Player where Player_id = " + pid);

        //get Player data from database
        ResultSet result = ps.executeQuery();

        result.next();

        name = result.getString("name");
        weight = result.getInt("weight");
        created_date = result.getDate("created_date");
        return this;
    }

    public List<Player> getPlayerList() throws SQLException {

        Connection con = dbConnect.getConnection();

        if (con == null) {
            throw new SQLException("Can't get database connection");
        }

        PreparedStatement ps
                = con.prepareStatement(
                        "select Player_id, name, address, created_date from Player order by Player_id");

        //get Player data from database
        ResultSet result = ps.executeQuery();

        List<Player> list = new ArrayList<Player>();

        while (result.next()) {
            Player cust = new Player();

            cust.setPlayerID(result.getInt("Player_id"));
            cust.setName(result.getString("name"));
            cust.setWeight(result.getInt("weight"));
            cust.setCreated_date(result.getDate("created_date"));

            //store all data into a List
            list.add(cust);
        }
        result.close();
        con.close();
        return list;
    }

    public void PlayerIDExists(FacesContext context, UIComponent componentToValidate, Object value)
            throws ValidatorException, SQLException {

        if (!existsPlayerId((Integer) value)) {
            FacesMessage errorMessage = new FacesMessage("ID does not exist");
            throw new ValidatorException(errorMessage);
        }
    }

    public void validatePlayerID(FacesContext context, UIComponent componentToValidate, Object value)
            throws ValidatorException, SQLException {
        int id = (Integer) value;
        if (id < 0) {
            FacesMessage errorMessage = new FacesMessage("ID must be positive");
            throw new ValidatorException(errorMessage);
        }
        if (existsPlayerId((Integer) value)) {
            FacesMessage errorMessage = new FacesMessage("ID already exists");
            throw new ValidatorException(errorMessage);
        }
    }

    private boolean existsPlayerId(int id) throws SQLException {
        Connection con = dbConnect.getConnection();
        if (con == null) {
            throw new SQLException("Can't get database connection");
        }

        PreparedStatement ps = con.prepareStatement("select * from Player where Player_id = " + id);

        ResultSet result = ps.executeQuery();
        if (result.next()) {
            result.close();
            con.close();
            return true;
        }
        result.close();
        con.close();
        return false;
    }
}