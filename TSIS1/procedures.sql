CREATE OR REPLACE PROCEDURE add_phone(p_name VARCHAR, p_phone VARCHAR, p_type VARCHAR) AS $$
BEGIN
    INSERT INTO phones (contact_id, phone, type)
    SELECT id, p_phone, p_type FROM contacts WHERE name = p_name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE move_to_group(p_name VARCHAR, p_group VARCHAR) AS $$
DECLARE v_id INT;
BEGIN
    INSERT INTO groups (name) VALUES (p_group) ON CONFLICT (name) DO NOTHING;
    SELECT id INTO v_id FROM groups WHERE name = p_group;
    UPDATE contacts SET group_id = v_id WHERE name = p_name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT) 
RETURNS TABLE(id INT, name VARCHAR, email VARCHAR, birthday DATE, group_name VARCHAR, phones TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.email, c.birthday, g.name, string_agg(ph.phone, ', ')
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones ph ON c.id = ph.contact_id
    WHERE c.name ILIKE '%' || p_query || '%' 
       OR c.email ILIKE '%' || p_query || '%'
       OR ph.phone ILIKE '%' || p_query || '%'
    GROUP BY c.id, g.name;
END;
$$ LANGUAGE plpgsql;
