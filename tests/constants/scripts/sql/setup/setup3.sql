CREATE TABLE users_sth (
	user_id INT UNSIGNED NOT NULL,
	sth_here VARCHAR(255),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
