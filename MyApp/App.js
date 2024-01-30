import { StatusBar } from 'expo-status-bar';
import SwiperCards from './components/SwiperCards';
import { StyleSheet, Text, View } from 'react-native';

const App = () => {
  return (
    <View style={styles.mainView}>
      < SwiperCards/>
    </View>
  );
}

const styles = StyleSheet.create({
  mainView: {
    flex: 1,
    justifyContent: 'center',
    backgroundColor: '#ecf0f1',
    alignItems: "center",
  },
});

export default App;