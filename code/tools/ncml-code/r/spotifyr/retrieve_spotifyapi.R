library('spotifyr')
#Sys.setenv(SPOTIFY_CLIENT_ID='XX')
#Sys.setenv(SPOTIFY_CLINET_SECRET='XX')
access_token <- get_spotify_access_token()

#---

Krenek <- get_artist_audio_features('Krenek')
IsSchickedanz <- grepl('Schickedanz', Krenek$artists, fixed=TRUE )
IsVioinsolo <- grepl('Sonata for Solo Violin No. 2', Krenek$track_name, fixed=TRUE)
T <-Krenek[IsSchickedanz&IsVioinsolo,]$tempo
mean(T)
sd(T)
(1000*60/mean(T))

Schickedanz <- get_artist_audio_features('Schickedanz')
IsBach <- grepl('Bach: Sonatas and Partitas for Solo Violin (Sei Solo á Violino senza Basso accompagnato)', Schickedanz$album_name, fixed=TRUE )
Schickedanz[IsBach,]
U <-Krenek[IsBach,]$tempo
mean(U)
sd(U)

(1000*60/mean(U))

c(60, 120, 240, 480, 960, 1820, 3640) / (1000*60/mean(U))
c(60, 120, 240, 480, 960, 1820, 3640) / (1000*60/mean(T))
